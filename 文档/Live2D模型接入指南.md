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

## 第三步：告诉我

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
