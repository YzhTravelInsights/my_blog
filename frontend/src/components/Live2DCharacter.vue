<!--
  萤宝 3D 虚拟人物组件

  Props:
    emotion  - 情绪动画模式
    modelPath - GLB 模型路径
    size     - 'small' | 'large'，控制交互方式
    greeting - 非空时显示气泡（外部控制）
-->
<template>
  <div
    ref="containerRef"
    class="three-d-container"
    :class="[`emotion-${emotion}`, `size-${size}`]"
    @click="handleClick"
  >
    <canvas ref="canvasRef" />
    <div v-if="loading" class="loading-overlay">✦</div>
    <div v-if="error" class="loading-overlay error">😵</div>

    <!-- 问候气泡 -->
    <Transition name="bubble">
      <div v-if="visibleGreeting" class="speech-bubble">
        {{ visibleGreeting }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'

const props = defineProps({
  emotion: { type: String, default: 'normal' },
  modelPath: { type: String, default: '/live2d/firefly/firefly.glb' },
  size: { type: String, default: 'small' }, // small | large
  greeting: { type: String, default: '' },
})

const emit = defineEmits(['click', 'loaded'])

const containerRef = ref(null)
const canvasRef = ref(null)
const loading = ref(true)
const error = ref(false)
const visibleGreeting = ref('')

// ---------------------------------------------------------------------------
// Three.js 状态
// ---------------------------------------------------------------------------
let renderer = null
let scene = null
let camera = null
let model = null
let rimLight = null
let halo = null      // 环绕粒子光环
let haloMat = null   // 光环材质（随情绪变色）
let animationId = null
let lastFrameTime = 0 // 帧节流用
const clock = new THREE.Clock()

let BASE_ROT_Y = 0 // 模型加载后设置为初始朝向

const animState = {
  emotion: 'normal',
  surprisedBurstAt: null,
  custom: null,
}

// ---------------------------------------------------------------------------
// 情绪动画配置
// ---------------------------------------------------------------------------
const ANIMS = {
  normal: {
    breatheAmp: 0.025,  breathFreq: 1.0,
    swayAmp: 0.12,      swayFreq: 0.3,
    floatAmp: 0.025,    floatFreq: 0.5,
    tiltAmp: 0.04,      tiltFreq: 0.4,
    lookAmp: 0.3,       lookFreq: 0.12,
    lightColor: 0xeef6f3, lightIntensity: 0.35,
    burstScale: 1,
  },
  happy: {
    breatheAmp: 0.03,   breathFreq: 2.0,
    swayAmp: 0.18,      swayFreq: 1.0,
    floatAmp: 0.05,     floatFreq: 2.0,
    tiltAmp: 0.06,      tiltFreq: 1.2,
    lookAmp: 0.2,       lookFreq: 0.5,
    lightColor: 0x8cf0b8, lightIntensity: 0.7,
    burstScale: 1,
  },
  thinking: {
    breatheAmp: 0.015,  breathFreq: 0.7,
    swayAmp: 0.2,       swayFreq: 0.25,
    floatAmp: 0.01,     floatFreq: 0.3,
    tiltAmp: 0.05,      tiltFreq: 0.25,
    lookAmp: 0.4,       lookFreq: 0.08,
    lightColor: 0x7cb8ff, lightIntensity: 0.55,
    burstScale: 1,
  },
  caring: {
    breatheAmp: 0.025,  breathFreq: 0.8,
    swayAmp: 0.08,      swayFreq: 0.25,
    floatAmp: 0.015,    floatFreq: 0.35,
    tiltAmp: 0.05,      tiltFreq: 0.3,
    lookAmp: 0.2,       lookFreq: 0.1,
    lightColor: 0xc8a8f0, lightIntensity: 0.5,
    burstScale: 1,
  },
  surprised: {
    breatheAmp: 0.035,  breathFreq: 3.0,
    swayAmp: 0.12,      swayFreq: 1.5,
    floatAmp: 0.06,     floatFreq: 3.5,
    tiltAmp: 0.07,      tiltFreq: 2.0,
    lookAmp: 0.15,      lookFreq: 1.0,
    lightColor: 0xeef6f3, lightIntensity: 0.7,
    burstScale: 1.25,
  },
}

// ---------------------------------------------------------------------------
// 问候语库（打招呼时随机选一句）
// ---------------------------------------------------------------------------
const GREETINGS = [
  '你好呀，开拓者～',
  '嘿！萤宝在这里哦！',
  '嘿嘿，你来啦～',
  '开拓者今天过得怎么样？',
  '萤宝等你很久了呢～',
  '哇，是开拓者！',
  '戳我干嘛呀～',
]

// 后台标签页暂停渲染，切回再续
function onVisibilityChange() {
  if (document.hidden) {
    if (animationId) { cancelAnimationFrame(animationId); animationId = null }
  } else if (!animationId && renderer) {
    lastFrameTime = performance.now()
    animate()
  }
}

function showGreeting() {
  const idx = Math.floor(Math.random() * GREETINGS.length)
  visibleGreeting.value = GREETINGS[idx]
  // 触发惊讶动画
  animState.surprisedBurstAt = clock.elapsedTime
  setTimeout(() => {
    visibleGreeting.value = ''
  }, 3000)
}

// ---------------------------------------------------------------------------
// 动画循环
// ---------------------------------------------------------------------------
function animate() {
  animationId = requestAnimationFrame(animate)
  // 30fps 节流：小角色不需要 60fps，省一半渲染开销
  const now = performance.now()
  if (now - lastFrameTime < 33) return
  lastFrameTime = now
  const t = clock.getElapsedTime()
  const cfg = ANIMS[animState.emotion] || ANIMS.normal

  if (model) {
    // —— 呼吸（身体起伏，幅度明显可见） ——
    const breathe = Math.sin(t * cfg.breathFreq) * cfg.breatheAmp
    model.scale.y = 1 + breathe
    model.scale.x = 1 + breathe * 0.4
    model.scale.z = 1 + breathe * 0.4

    // —— 上下浮动（身体像站在波浪上） ——
    const f1 = Math.sin(t * cfg.floatFreq) * cfg.floatAmp
    const f2 = Math.sin(t * cfg.floatFreq * 1.7 + 1.2) * cfg.floatAmp * 0.6
    model.position.y = f1 + f2

    // —— 左右摇摆（身体 sway，像在轻轻晃动） ——
    const s1 = Math.sin(t * cfg.swayFreq) * cfg.swayAmp
    const s2 = Math.sin(t * cfg.swayFreq * 0.5 + 0.8) * cfg.swayAmp * 0.5
    model.rotation.z = s1 + s2

    // —— 前后倾斜（身体微微俯仰） ——
    model.rotation.x = Math.sin(t * cfg.tiltFreq) * cfg.tiltAmp

    // —— 转头环顾（在初始角度上左右摆动） ——
    model.rotation.y = BASE_ROT_Y + Math.sin(t * cfg.lookFreq) * cfg.lookAmp

    // —— 周期性大动作（每 4-6 秒一次） ——
    const bigMoveCycle = 4.5 // 秒
    const bigPhase = (t % bigMoveCycle) / bigMoveCycle
    if (bigPhase > 0.85 && bigPhase < 0.95) {
      // 每周期一次小跳跃/起伏
      const p = (bigPhase - 0.85) / 0.1 // 0→1
      const ease = 1 - Math.pow(1 - p, 2) // ease-out
      model.position.y += Math.sin(ease * Math.PI) * 0.04
      model.scale.y += Math.sin(ease * Math.PI) * 0.015
    }

    // —— 惊讶爆发 ——
    if (animState.surprisedBurstAt !== null) {
      const bt = t - animState.surprisedBurstAt
      if (bt < 0.5) {
        const f = Math.max(0, 1 - bt / 0.3)
        const burst = 1 + (cfg.burstScale - 1) * f * f
        model.scale.x *= burst
        model.scale.y *= burst
        model.scale.z *= burst
        model.position.y += 0.04 * f
      } else {
        animState.surprisedBurstAt = null
      }
    }
  }

  // —— 情绪色氛围光 ——
  if (rimLight) {
    rimLight.color.setHex(cfg.lightColor)
    rimLight.intensity = cfg.lightIntensity
  }

  // —— 环绕光环：缓慢旋转 + 随情绪变色 ——
  if (halo) {
    halo.rotation.y += 0.0045
    if (haloMat) haloMat.color.setHex(cfg.lightColor)
  }

  if (renderer && scene && camera) {
    renderer.render(scene, camera)
  }
}

// ---------------------------------------------------------------------------
// 生命周期
// ---------------------------------------------------------------------------
onMounted(() => {
  const container = containerRef.value
  const canvas = canvasRef.value
  if (!container || !canvas) return

  const w = container.clientWidth
  const h = container.clientHeight
  if (w === 0 || h === 0) return

  const isLarge = props.size === 'large'

  // —— 场景 ——
  scene = new THREE.Scene()

  // —— 相机 ——
  const fov = isLarge ? 32 : 35
  const dist = isLarge ? 3.2 : 2.8
  camera = new THREE.PerspectiveCamera(fov, w / h, 0.1, 100)
  camera.position.set(0, 0.3, dist)
  camera.lookAt(0, 0.3, 0)

  // —— 渲染器 ——
  renderer = new THREE.WebGLRenderer({
    canvas,
    alpha: true,
    antialias: true,
    powerPreference: 'high-performance',
  })
  renderer.setSize(w, h)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.0
  renderer.outputColorSpace = THREE.SRGBColorSpace

  // —— 灯光 ——
  scene.add(new THREE.AmbientLight(0xffffff, 0.5))
  const hemi = new THREE.HemisphereLight(0x87ceeb, 0x362907, 0.6)
  scene.add(hemi)

  const main = new THREE.DirectionalLight(0xffffff, 1.0)
  main.position.set(3, 5, 4)
  scene.add(main)

  const fill = new THREE.DirectionalLight(0x8888ff, 0.3)
  fill.position.set(-3, 2, 2)
  scene.add(fill)

  const back = new THREE.DirectionalLight(0x4466ff, 0.15)
  back.position.set(0, 1, -3)
  scene.add(back)

  rimLight = new THREE.DirectionalLight(0x93c5fd, 0.25)
  rimLight.position.set(2, 1, -2)
  scene.add(rimLight)

  // —— 环绕粒子光环（萤火星云） ——
  const haloCount = isLarge ? 34 : 24
  const haloRadius = isLarge ? 1.45 : 1.2
  const haloPos = new Float32Array(haloCount * 3)
  for (let i = 0; i < haloCount; i++) {
    const angle = (i / haloCount) * Math.PI * 2
    const r = haloRadius + (Math.random() - 0.5) * 0.18
    haloPos[i * 3] = Math.cos(angle) * r
    haloPos[i * 3 + 1] = 0.3 + (Math.random() - 0.5) * 1.0
    haloPos[i * 3 + 2] = Math.sin(angle) * r
  }
  const haloGeo = new THREE.BufferGeometry()
  haloGeo.setAttribute('position', new THREE.Float32BufferAttribute(haloPos, 3))
  haloMat = new THREE.PointsMaterial({
    color: 0x8cf0b8,
    size: isLarge ? 0.04 : 0.032,
    transparent: true,
    opacity: 0.8,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    sizeAttenuation: true,
  })
  halo = new THREE.Points(haloGeo, haloMat)
  halo.rotation.x = Math.PI / 2.4 // 略微倾斜成环带
  scene.add(halo)

  // —— 加载模型 ——
  const loader = new GLTFLoader()
  loader.load(
    props.modelPath,
    (gltf) => {
      model = gltf.scene
      const box = new THREE.Box3().setFromObject(model)
      const center = box.getCenter(new THREE.Vector3())
      model.position.sub(center)
      const size = box.getSize(new THREE.Vector3())
      const maxDim = Math.max(size.x, size.y, size.z)
      const targetH = isLarge ? 2.0 : 1.8
      const s = targetH / maxDim
      model.scale.set(s, s, s)
      BASE_ROT_Y = -Math.PI / 2
      model.rotation.y = BASE_ROT_Y

      scene.add(model)
      loading.value = false
      emit('loaded')
    },
    undefined,
    () => {
      loading.value = false
      error.value = true
    },
  )

  document.addEventListener('visibilitychange', onVisibilityChange)

  animate()
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  document.removeEventListener('visibilitychange', onVisibilityChange)
  if (halo) {
    halo.geometry?.dispose()
    haloMat?.dispose()
    halo = null
    haloMat = null
  }
  if (renderer) {
    renderer.dispose()
    renderer = null
  }
  if (scene) {
    scene.traverse((n) => {
      if (n.isMesh) {
        n.geometry?.dispose()
        if (n.material) {
          ;(Array.isArray(n.material) ? n.material : [n.material]).forEach((m) => m.dispose())
        }
      }
    })
  }
  scene = null; model = null
})

// ---------------------------------------------------------------------------
// 监听 emotion 变化
// ---------------------------------------------------------------------------
watch(() => props.emotion, (emo) => {
  animState.emotion = emo
  if (emo === 'surprised') animState.surprisedBurstAt = clock.elapsedTime
})

// 监听 greeting 变化（外部触发）
watch(() => props.greeting, (val) => {
  if (val) showGreeting()
})

function handleClick() {
  showGreeting()
  emit('click')
}
</script>

<style scoped>
.three-d-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  cursor: pointer;
}
.three-d-container canvas {
  display: block;
  width: 100% !important;
  height: 100% !important;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #93c5fd;
  background: rgba(255, 255, 255, 0.5);
  border-radius: inherit;
  animation: spin 1s linear infinite;
}
.loading-overlay.error {
  font-size: 14px;
  color: #f87171;
  animation: none;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* —— 问候气泡 —— */
.speech-bubble {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  color: #334155;
  font-size: 13px;
  padding: 6px 14px;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
  white-space: nowrap;
  z-index: 10;
  pointer-events: none;
}
.speech-bubble::after {
  content: '';
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  width: 0; height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 6px solid white;
}

/* 气泡进出动画 */
.bubble-enter-active { animation: popIn 0.25s ease-out; }
.bubble-leave-active { animation: popOut 0.2s ease-in; }
@keyframes popIn {
  0% { opacity: 0; transform: translateX(-50%) scale(0.7) translateY(4px); }
  100% { opacity: 1; transform: translateX(-50%) scale(1) translateY(0); }
}
@keyframes popOut {
  0% { opacity: 1; transform: translateX(-50%) scale(1); }
  100% { opacity: 0; transform: translateX(-50%) scale(0.7) translateY(-4px); }
}

/* 情绪色光圈（萤火绿 / 星蓝 / 薰衣草 / 柔白） */
.emotion-happy { filter: drop-shadow(0 0 7px rgba(140,240,184,0.55)); }
.emotion-thinking { filter: drop-shadow(0 0 7px rgba(124,184,255,0.55)); }
.emotion-caring { filter: drop-shadow(0 0 7px rgba(200,168,240,0.55)); }
.emotion-surprised { filter: drop-shadow(0 0 7px rgba(238,246,243,0.6)); }
</style>
