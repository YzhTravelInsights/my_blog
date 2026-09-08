<!--
  萤火粒子背景：Canvas 上少量半透明光点缓慢上浮，营造「萤火星云」氛围。
  - fixed inset-0、z-index 最低、pointer-events-none，绝不挡交互
  - 性能优化：预渲染光点贴图（drawImage，无逐粒子 shadowBlur）、
    DPR 上限 1.5、30fps 节流、后台标签页暂停渲染
  - 深色模式粒子更亮、浅色模式更淡（--particle-opacity 语义）
  - prefers-reduced-motion 时只画一帧静态，不做动画
-->
<template>
  <canvas ref="canvasRef" class="particle-bg" aria-hidden="true" />
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const canvasRef = ref(null)
let ctx = null
let raf = null
let width = 0
let height = 0
let particles = []
let animating = false
let lastDraw = 0
let sprite = null // 预渲染的光点贴图（白色径向渐变）

const COLORS = ['140,240,184', '124,184,255', '200,168,240'] // 萤火绿 / 星蓝 / 薰衣草
const reducedMotion =
  typeof window !== 'undefined' &&
  !!window.matchMedia?.('(prefers-reduced-motion: reduce)').matches

// 预渲染一颗光点贴图（避免每帧对每颗粒子开 shadowBlur，开销极高）
function makeSprite() {
  sprite = document.createElement('canvas')
  sprite.width = 64
  sprite.height = 64
  const sctx = sprite.getContext('2d')
  if (!sctx) return
  const g = sctx.createRadialGradient(32, 32, 0, 32, 32, 32)
  g.addColorStop(0, 'rgba(255,255,255,1)')
  g.addColorStop(0.35, 'rgba(255,255,255,0.5)')
  g.addColorStop(1, 'rgba(255,255,255,0)')
  sctx.fillStyle = g
  sctx.fillRect(0, 0, 64, 64)
}

function initParticles(count) {
  particles = []
  for (let i = 0; i < count; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      r: Math.random() * 2.2 + 0.8,
      color: COLORS[Math.floor(Math.random() * COLORS.length)],
      vx: (Math.random() - 0.5) * 0.16,
      vy: -(Math.random() * 0.2 + 0.05),
      alpha: Math.random() * 0.5 + 0.25,
      phase: Math.random() * Math.PI * 2,
      twinkle: Math.random() * Math.PI * 2,
    })
  }
}

function drawFrame() {
  if (!sprite) return
  ctx.clearRect(0, 0, width, height)
  // 随明暗切换调整亮度
  const isDark = document.documentElement.classList.contains('dark')
  const base = isDark ? 0.9 : 0.5
  ctx.globalCompositeOperation = 'lighter'

  for (const p of particles) {
    p.x += p.vx + Math.sin(p.phase) * 0.05
    p.y += p.vy
    p.phase += 0.006
    p.twinkle += 0.035
    if (p.y < -12) { p.y = height + 12; p.x = Math.random() * width }
    if (p.x < -12) p.x = width + 12
    else if (p.x > width + 12) p.x = -12

    const tw = 0.5 + 0.5 * Math.sin(p.twinkle)
    const a = p.alpha * tw * base
    if (a <= 0.01) continue
    const size = p.r * 6
    ctx.globalAlpha = a
    ctx.drawImage(sprite, p.x - size, p.y - size, size * 2, size * 2)
  }
  ctx.globalAlpha = 1
  ctx.globalCompositeOperation = 'source-over'
}

function draw() {
  if (!animating) return
  raf = requestAnimationFrame(draw)
  // 30fps 节流：攒够时间才重绘，明显减负且视觉差异很小
  const now = performance.now()
  if (now - lastDraw < 33) return
  lastDraw = now
  drawFrame()
}

function start() {
  if (animating || reducedMotion || !ctx) return
  animating = true
  draw()
}

function stop() {
  animating = false
  if (raf) cancelAnimationFrame(raf)
}

function onVisibility() {
  if (document.hidden) stop()
  else start()
}

function resize() {
  const dpr = Math.min(window.devicePixelRatio || 1, 1.5) // 高 DPR 下像素减半，光点本就柔和
  width = window.innerWidth
  height = window.innerHeight
  const canvas = canvasRef.value
  if (!canvas) return
  canvas.width = Math.floor(width * dpr)
  canvas.height = Math.floor(height * dpr)
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  // 光点密度随屏幕面积变化，控制在上限内
  const count = Math.min(50, Math.max(18, Math.floor((width * height) / 30000)))
  initParticles(count)
}

onMounted(() => {
  const canvas = canvasRef.value
  if (!canvas) return
  ctx = canvas.getContext('2d')
  if (!ctx) return // 测试环境等无 2d 上下文时静默跳过
  makeSprite()
  resize()
  window.addEventListener('resize', resize)
  document.addEventListener('visibilitychange', onVisibility)
  if (reducedMotion) {
    drawFrame() // 只画一帧静态
  } else {
    start()
  }
})

onUnmounted(() => {
  stop()
  window.removeEventListener('resize', resize)
  document.removeEventListener('visibilitychange', onVisibility)
})
</script>

<style scoped>
.particle-bg {
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
}
</style>
