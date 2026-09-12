# Live2D 萤宝模型接入指南

> **当前状态**：静态图片 + CSS 动画（`frontend/public/firefly-avatar.png`）
> **目标状态**：真正的 Live2D 模型——呼吸、眨眼、挥手、随情绪切换动作

---

## 概述

你需要在 `frontend/public/live2d/firefly/` 目录下准备好一套 Live2D 模型文件，
然后我这边改一行代码即可接入。整个过程分两步：**找/做模型** → **我接入代码**。

---

## 第一步：获取模型文件

### 方法一：下载免费 Live2D 模型（推荐起步）

适合先跑通流程，后续再换定制模型。

**资源站**：
| 站点 | 地址 | 说明 |
|------|------|------|
| Live2D 官方示例 | https://www.live2d.com/en/download/sample-data/ | 官方免费示例，质量极高 |
| Booth.pm | https://booth.pm/ | 搜索 `Live2D フリー` 或 `live2d free` |
| Nizima | https://nizima.com/ | Live2D 模型 marketplace |

**搜索关键词**：`銀髪 少女 Live2D フリー` / `white hair anime girl live2d free model`

**下载后确认**：解压后必须有 `.model3.json` 文件（或 `.moc3.json`）。

### 方法二：用 VRoid Studio 自制（可捏脸）

1. Steam 免费下载 [VRoid Studio](https://store.steampowered.com/app/1481000/VRoid_Studio/)
2. 捏一个银发少女（萤宝）
3. 导出 `.vrm` 文件
4. 用 [vrm2live2d](https://github.com/ColinHarker/vrm2live2d) 转换为 Live2D 格式

> 效果取决于你的捏脸功力和转换工具质量。

### 方法三：Live2D Cubism Editor 从零制作

需要专业绘画功底 + 学习 Live2D 骨骼绑定，通常需要数周到数月。适合有美术基础的开发者。

---

## 第二步：文件放置

拿到模型后，目录结构如下：

```
frontend/public/live2d/firefly/
├── firefly.model3.json        ← 必需！模型配置文件
├── firefly.2048/              ← 贴图目录（也可能是 1024）
│   └── texture_00.png         ← 角色贴图
├── motions/                   ← 动作文件（可选，没有也能动）
│   ├── idle.motion3.json      ← 待机（呼吸+眨眼）
│   ├── wave.motion3.json      ← 挥手（点击时触发）
│   ├── happy.motion3.json     ← 开心
│   └── think.motion3.json     ← 思考
└── firefly.physics3.json      ← 物理模拟（头发/裙子摇摆，可选）
```

**最简要求**：至少要有 `.model3.json` + 贴图目录。动作文件和物理文件是加分项。

---

## 第三步：情绪-动作映射规格（重要！制作模型前必读）

这是整个 Live2D 集成的核心——**后端 API 返回 emotion → 前端 Live2D 播放对应动作**。

### 3.1 情绪-动作对照表

| emotion | motion group | 动作效果 | 触发时机 | 情绪色 |
|---------|-------------|---------|---------|-------|
| `normal` | `Idle` | 呼吸浮动 + 眨眼循环 | 默认待机状态、无特殊情绪回复 | — |
| `happy` | `Happy` | 身体轻快上跳 + 挥手/拍手 + 眯眼笑 | 夸奖、开心、收到好消息 | 🟡 金色 |
| `thinking` | `Thinking` | 歪头 + 手指点下巴 + 眼神上移 | 被问到技术问题、RAG 检索中 | 🟣 紫色 |
| `caring` | `Caring` | 身体前倾 + 双手交握胸前 + 温柔歪头 | 用户表达负面情绪、安慰场景 | 🩷 粉色 |
| `surprised` | `Surprised` | 身体后仰 + 眼睛瞪大 + 嘴巴微张 | 新发现、有趣的事、好消息 | 🔵 蓝色 |

> **注意**：`Idle` 是 Live2D SDK 保留的特殊 group——模型加载后自动循环播放，不需要手动触发。

### 3.2 动作在模型文件中的约定

Live2D 用 **motion group 名称**来组织动作。你在 Cubism Editor 中导出时，motion group 名必须与上表一致（大小写敏感）：

```
motions/
├── Idle.motion3.json       ← group: "Idle"      （自动循环，呼吸+眨眼）
├── Happy.motion3.json      ← group: "Happy"     （开心挥手）
├── Thinking.motion3.json   ← group: "Thinking"  （歪头思考）
├── Caring.motion3.json     ← group: "Caring"    （温柔关心）
└── Surprised.motion3.json  ← group: "Surprised" （惊讶）
```

### 3.3 逐动作制作规格（Cubism Editor）

以下是你需要在 Cubism Editor 中为每个动作绑定的参数和时间轴：

#### Idle（待机呼吸）

```
目的：模型在无操作时的自然循环

▎ 参数设置
├─ PARAM_ANGLE_X:     0              （不歪头）
├─ PARAM_ANGLE_Y:     0 → +2 → 0     （轻微上下点头，周期 4s）
├─ PARAM_BODY_ANGLE_X: 0             （身体不转）
├─ PARAM_BREATH:      0 → +1 → 0 → -1 → 0  （呼吸起伏，周期 6s）
├─ PARAM_EYE_L_OPEN:  1              （眼睛正常睁开）
├─ PARAM_EYE_R_OPEN:  1
└─ 眨眼（每 4-6s 一次）:
   ├─ 0.00s:  PARAM_EYE_L/R_OPEN = 1
   ├─ 0.05s:  PARAM_EYE_L/R_OPEN = 0   （闭眼）
   ├─ 0.10s:  PARAM_EYE_L/R_OPEN = 1   （睁眼）
   └─ 循环

▎ 循环设置
├─ Loop: true（无限循环）
├─ 单次时长: ~6s
└─ 优先级: 0（最低，可被其他动作打断）
```

#### Happy（开心/高兴）

```
目的：表达积极情绪

▎ 参数设置
├─ PARAM_ANGLE_X:     0
├─ PARAM_ANGLE_Y:     0 → -3 → 0     （轻轻后仰）
├─ PARAM_BODY_ANGLE_X: 0
├─ PARAM_BODY_Y:      0 → -10 → 0    （身体上跳离开画面，配合"跳"的感觉）
├─ PARAM_EYE_L_OPEN:  1 → 0.7 → 1   （眯眼笑，微闭）
├─ PARAM_EYE_R_OPEN:  1 → 0.7 → 1
├─ PARAM_MOUTH_FORM:  0 → 1 → 0      （张嘴笑）
├─ PARAM_BREATH:      0 → 0.5 → 0    （略急促）
└─ 手部（如果有手部骨骼）:
   ├─ 右臂稍微抬起到胸前 → 摆动几下（挥手效果）
   └─ 或：双手在胸前轻轻拍一下

▎ 循环设置
├─ Loop: false（播放一次即回 Idle）
├─ 单次时长: ~2-3s
├─ 过渡时间: 0.3s
└─ 优先级: 1
```

#### Thinking（思考）

```
目的：被问到技术问题时的思考状态

▎ 参数设置
├─ PARAM_ANGLE_X:     0 → +5 → 0     （头向右歪）
├─ PARAM_ANGLE_Y:     0 → -2 → 0     （微微抬起，眼神上移作思考状）
├─ PARAM_BODY_ANGLE_X: 0
├─ PARAM_EYE_L_OPEN:  1 → 0.3 → 1   （眼睛微眯，聚焦状态）
├─ PARAM_EYE_R_OPEN:  1 → 0.3 → 1
├─ PARAM_EYE_BALL_X:  0 → +3 → 0     （眼珠向右转动，表示思考）
├─ PARAM_EYE_BALL_Y:  0 → +2 → 0     （眼珠微微上翻）
├─ PARAM_MOUTH_FORM:  0              （嘴角微抿或不动）
└─ 手部（推荐，但可选）:
   └─ 右手抬起到下巴附近，食指轻点下巴/嘴角

▎ 循环设置
├─ Loop: false
├─ 单次时长: ~3-4s
├─ 过渡时间: 0.5s（慢一点，突出"正在想"）
└─ 优先级: 1
```

#### Caring（关心/安慰）

```
目的：用户表达负面情绪时的温柔回应

▎ 参数设置
├─ PARAM_ANGLE_X:     0 → +3 → 0     （头轻轻歪向一侧）
├─ PARAM_ANGLE_Y:     0 → -5 → 0     （低头，表示关切/俯视）
├─ PARAM_BODY_ANGLE_X: 0 → -2 → 0    （身体微微前倾）
├─ PARAM_BODY_Y:      0 → +2 → 0     （轻微前移）
├─ PARAM_EYE_L_OPEN:  1 → 0.5 → 1   （眼神温柔，半闭状态）
├─ PARAM_EYE_R_OPEN:  1 → 0.5 → 1
├─ PARAM_EYE_BALL_Y:  0 → -2 → 0     （视线向下，看对方）
├─ PARAM_BREATH:      0 → 0.3 → 0    （轻柔缓慢呼吸）
└─ 手部（推荐）:
   └─ 双手在胸前轻轻交握（表达关心/支持）

▎ 循环设置
├─ Loop: false
├─ 单次时长: ~3s
├─ 过渡时间: 0.5s
└─ 优先级: 2（高于 happy/thinking，安慰优先）
```

#### Surprised（惊讶）

```
目的：听到意外消息时的反应

▎ 参数设置
├─ PARAM_ANGLE_X:     0
├─ PARAM_ANGLE_Y:     0 → +4 → 0     （身体后仰/抬头）
├─ PARAM_BODY_ANGLE_X: 0 → -3 → 0    （身体微微后退）
├─ PARAM_BODY_Y:      0 → +5 → 0     （向上跳/惊了一下）
├─ PARAM_EYE_L_OPEN:  1 → 1.5 → 1   （眼睛睁大 > 100%，夸张效果）
├─ PARAM_EYE_R_OPEN:  1 → 1.5 → 1
├─ PARAM_MOUTH_FORM:  0 → 1.5 → 0   （嘴巴张大呈 O 型）
├─ PARAM_BREATH:      0 → 1 → 0      （深吸一口气）
└─ 可选加速:
   └─ 所有参数过渡时间缩短到 0.1-0.15s（快速反应）

▎ 循环设置
├─ Loop: false
├─ 单次时长: ~1.5-2s（短促有力）
├─ 过渡时间: 0.1s（快速爆发）
└─ 优先级: 3（惊讶需要立即表现）
```

### 3.4 动作优先级系统

多个动作同时请求时的优先级（数字越大越优先）：

| 优先级 | 动作 | 说明 |
|--------|------|------|
| 0 | Idle | 待机循环，优先级最低 |
| 1 | Happy / Thinking | 常规情绪表达 |
| 2 | Caring | 安慰场景需要及时响应 |
| 3 | Surprised | 惊讶需要立即打断当前动作 |

> Cubism SDK 原生支持优先级调度——代码中设置 `priority` 参数即可。高优先级自动打断低优先级动作。

### 3.5 点击交互动作（额外福利）

除了情绪驱动，Live2D 模型还应支持**点击交互**——用户在萤宝头像上点击时触发一个"回应"动作。

建议方案：

| 交互 | 动作 | 说明 |
|------|------|------|
| 点击头像 | `Tap.motion3.json` | 身体微动 + 挥手 + 说"嗯？" |
| 鼠标悬停 | 脸微红（表情参数） | 不改变 motion，仅调参数 |

> 这不是必需功能，但加上后体验更好。如果时间和精力允许，可以额外制作一个 `Tap` 动作。

### 3.6 表情参数 vs 动作文件的取舍

如果你时间有限、不想做 5 个独立的 `.motion3.json`，可以用**简化方案**——只做 1 个 Idle 动作，通过调整表情参数（Expression）来实现情绪变化：

```
model3.json 中注册表情：
expressions/
├── exp_normal.json       ← PARAM_EYE_L/R_OPEN 正常
├── exp_happy.json        ← 眯眼笑 0.7 + 嘴角上扬
├── exp_thinking.json     ← 歪头 + 眼神偏移
├── exp_caring.json       ← 半闭眼 + 低头
└── exp_surprised.json    ← 睁大眼 + 张嘴
```

对应关系：

| 等级 | 实现方式 | 工作量 | 效果 |
|------|---------|--------|------|
| ⭐ 基础 | 仅 Idle motion + 5 个 Expression | 低 | 只变表情，身体不动笔 |
| ⭐⭐ 标准 | 5 个 motion（Idle+4情绪） | 中 | 身体动作 + 表情联动 |
| ⭐⭐⭐ 完整 | 5 motion + 物理 + 点击交互 + 唇形同步 | 高 | 完全体，可用于直播 |

> **推荐标准方案**——在 Cubism Editor 中为每个情绪单独做一个 short motion（2-3s），同时设定表情参数，效果和性能平衡最好。

---

## 第四步：代码调用链路（开发者视角）

这是 emotion 从后端 API 到前端 Live2D 动画的完整数据流：

```
┌─────────────────────────────────────────────────────────────────┐
│                       1. 用户输入消息                            │
│                          │                                       │
│                         ▼                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  ChatWidget.vue: sendMessage() → POST /api/chat         │   │
│   └──────────────────────┬──────────────────────────────────┘   │
│                          │                                       │
│                         ▼                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  backend: chat/service.py                                │   │
│   │  ├─ DeepSeek 生成回复文本                                │   │
│   │  └─ _detect_emotion(reply) → "happy"                    │   │
│   └──────────────────────┬──────────────────────────────────┘   │
│                          │                                       │
│                         ▼                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  API 响应: { reply: "...", emotion: "happy", ... }     │   │
│   └──────────────────────┬──────────────────────────────────┘   │
│                          │                                       │
│                         ▼                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  ChatWidget.vue:                                         │   │
│   │  ├─ 收到响应, push 到 messages                           │   │
│   │  └─ lastEmotion = messages.last().emotion                │   │
│   └──────────────────────┬──────────────────────────────────┘   │
│                          │                                       │
│                         ▼                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  Live2DCharacter.vue:                                    │   │
│   │  ├─ props.emotion = "happy"                             │   │
│   │  └─ watch(emotion) → model.motion("Happy", priority=1) │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   Live2D 模型: 播放 Happy.motion3.json                          │
│   ─→ 身体上跳 + 挥手 + 眯眼笑 (~2s)                           │
│   ─→ 播放完毕后自动回到 Idle 循环                               │
└─────────────────────────────────────────────────────────────────┘
```

### 4.1 后端情绪检测（已有，无需修改）

`backend/modules/chat/service.py` 中的 `_detect_emotion()` 通过关键词匹配判断情绪：

```python
def _detect_emotion(text: str) -> str:
    happy_words = ["哈哈", "嘿嘿", "太好了", "棒", "开心", "厉害", "喜欢"]
    thinking_words = ["唔", "让我想想", "这个嘛", "嗯..."]
    caring_words = ["没关系", "别担心", "辛苦", "抱抱", "没事的"]
    # ... 匹配返回 "happy" / "thinking" / "caring" / "normal"
```

> **后续可升级**：让 DeepSeek 直接在响应中返回 `emotion` 字段，比关键词匹配更准确。

### 4.2 前端 Live2DCharacter.vue 接入后的伪代码

当你准备好模型文件后，`Live2DCharacter.vue` 会改成这样：

```javascript
// Live2DCharacter.vue（Live2D 版本）
import * as PIXI from 'pixi.js'
import { Live2DModel } from 'pixi-live2d-display'

// emotion → motion group 映射
const EMOTION_MOTION_MAP = {
  normal:    { group: 'Idle',       priority: 0 },
  happy:     { group: 'Happy',      priority: 1 },
  thinking:  { group: 'Thinking',   priority: 1 },
  caring:    { group: 'Caring',     priority: 2 },
  surprised: { group: 'Surprised',  priority: 3 },
}

const props = defineProps({
  emotion: { type: String, default: 'normal' },
  modelPath: { type: String, default: '/live2d/firefly/firefly.model3.json' },
})

// 加载模型
const app = new PIXI.Application({ view: canvas, width: 200, height: 200 })
const model = await Live2DModel.from(props.modelPath, { autoInteract: false })
app.stage.addChild(model)

// 监听 emotion 变化 → 播放对应动作
watch(() => props.emotion, (newEmo) => {
  const { group, priority } = EMOTION_MOTION_MAP[newEmo]
  model.motion(group, priority)
  // 非 Idle 动作播放完毕后自动回到 Idle（Cube 5 SDK 行为）
})

// 点击交互
model.on('hit', (hitAreaName) => {
  model.motion('Tap', 3)  // 优先级 3，立即打断当前动作
})
```

### 4.3 与 ChatWidget 的联动（已有，无需修改）

`ChatWidget.vue` 已经正确连接了 Live2DCharacter：

```html
<!-- ChatWidget.vue 中已存在的正确写法 -->
<Live2DCharacter :emotion="lastEmotion" />

<!-- 其中 lastEmotion 自动取最后一条助手回复的情绪 -->
const lastEmotion = computed(() => {
  const last = messages.value.filter(m => m.role === 'assistant').at(-1)
  return last?.emotion || 'normal'
})
```

**无需修改 ChatWidget.vue**——它已经把 emotion 传给 Live2DCharacter 了。接入Live2D 只需要改 `Live2DCharacter.vue` 一个文件。

### 4.4 model3.json 中注册 motion

你的 `firefly.model3.json` 需要包含以下配置来注册动作文件：

```json
{
  "Version": 3,
  "FileReferences": {
    "Moc": "firefly.moc3",
    "Textures": ["firefly.2048/texture_00.png"],
    "Motions": {
      "Idle": [
        { "File": "motions/Idle.motion3.json", "Loop": true }
      ],
      "Happy": [
        { "File": "motions/Happy.motion3.json", "Loop": false }
      ],
      "Thinking": [
        { "File": "motions/Thinking.motion3.json", "Loop": false }
      ],
      "Caring": [
        { "File": "motions/Caring.motion3.json", "Loop": false }
      ],
      "Surprised": [
        { "File": "motions/Surprised.motion3.json", "Loop": false }
      ]
    },
    "Expressions": [
      { "File": "expressions/exp_normal.json" },
      { "File": "expressions/exp_happy.json" },
      { "File": "expressions/exp_thinking.json" },
      { "File": "expressions/exp_caring.json" },
      { "File": "expressions/exp_surprised.json" }
    ],
    "Physics": "firefly.physics3.json"
  },
  "Groups": [
    {
      "Target": "Parameter",
      "Name": "EyeBlink",
      "Ids": ["PARAM_EYE_L_OPEN", "PARAM_EYE_R_OPEN"]
    },
    {
      "Target": "Parameter",
      "Name": "LipSync",
      "Ids": ["PARAM_MOUTH_FORM"]
    }
  ]
}
```

> `Motions` 中每个 key（Idle/Happy/Thinking/...）就是 **motion group 名称**，代码中的 `model.motion(group, priority)` 通过这个名称匹配。

---

## 第五步：告诉我

把模型放到 `frontend/public/live2d/firefly/` 后，告诉我以下信息：

1. **模型来源**：免费下载 / VRoid 制作 / 自己画
2. **文件列表**：有哪些 `.json` 和贴图文件
3. **动作文件**：有没有 motions/ 目录

然后我改 `Live2DCharacter.vue`，把 `pixi-live2d-display` 接上，5 分钟搞定。

---

## 技术方案说明（给你看的，不用操作）

接入后的组件结构：

```javascript
// Live2DCharacter.vue (Live2D 版本)
import * as PIXI from 'pixi.js'
import { Live2DModel } from 'pixi-live2d-display'

// 1. 创建 PIXI 画布
// 2. Live2DModel.from(modelPath) 加载模型
// 3. model.motion('idle') 播放待机
// 4. watch(emotion) → model.motion(emotion) 切换动作
// 5. 点击 → model.motion('wave')
```

需要的前端依赖（`npm install`）：
- `pixi.js` — WebGL 渲染引擎
- `pixi-live2d-display` — Live2D 模型加载器

---

## 临时方案说明

在模型就绪前，`Live2DCharacter.vue` 使用 `frontend/public/firefly-avatar.png` 作为静态头像，
配合 CSS 关键帧动画模拟 5 种情绪：

| emotion | 动画效果 | 视觉 |
|---------|---------|------|
| normal | 呼吸缩放 | 柔和缩放 |
| happy | 弹跳 + 金色光晕 | 活跃弹跳 |
| thinking | 左右轻摇 + 紫色光晕 | 思考状 |
| caring | 心跳脉冲 + 粉色光晕 | 温柔脉动 |
| surprised | 两次大幅度缩放 + 蓝色光晕 | 惊讶 |

---

## 回到这个对话

如果你因为做模型中断了几天，开新对话时这样说：

```
我在开发个人博客项目，技术文档在 文档/技术设计文档.md。

Live2D 模型已经准备好了，文件放在 frontend/public/live2d/firefly/。
请阅读 文档/Live2D模型接入指南.md，
然后把 Live2DCharacter.vue 改成 pixi-live2d-display 版本接入真实模型。

当前分支是 master，先开新分支 feature/live2d。
```

我会自动理解上下文并继续。
