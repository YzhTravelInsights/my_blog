---
title: "Tailwind CSS 4 主题定制实战：用 @theme 打造暗色主题"
date: 2026-07-05
category: 前端
tags: ["TailwindCSS", "CSS变量", "主题"]
summary: "手把手讲解 Tailwind CSS 4 如何用 @theme 与 CSS 变量实现明暗双主题，并封装磨砂玻璃卡片组件类。"
---

## 引言

Tailwind CSS 4 移除了传统的 `tailwind.config.js`，主题定制直接写在 CSS 里。这让「用 CSS 变量驱动明暗切换」变得前所未有的顺滑。

## 设计令牌先行

### 什么是设计令牌

设计令牌就是一组命名的、复用的样式值。比如把主色命名为 `primary`，把背景命名为 `bg-base`。

### 定义语义变量

```css
:root {
  --c-primary: #8cf0b8;
  --c-surface: rgba(255, 255, 255, 0.55);
  --c-ink: #1f2937;
}

.dark {
  --c-primary: #8cf0b8;
  --c-surface: rgba(255, 255, 255, 0.04);
  --c-ink: #eef6f3;
}
```

## 映射到 @theme

```css
@import "tailwindcss";

@theme {
  --color-primary: var(--c-primary);
  --color-ink: var(--c-ink);
  --color-surface: var(--c-surface);
}
```

这样就能在模板里直接写 `bg-primary`、`text-ink`、`bg-surface`，且颜色随明暗自动切换。

### 封装组件类

把重复的玻璃卡片样式抽成组件类，保持模板干净：

```css
@layer components {
  .glass-card {
    @apply rounded-2xl backdrop-blur-xl border border-border-soft bg-surface;
  }
}
```

## 明暗切换逻辑

切换的本质只是给 `<html>` 加/去 `.dark`：

```js
function toggle() {
  document.documentElement.classList.toggle('dark')
}
```

## 小结

Tailwind 4 + CSS 变量 是当前做主题最顺手的组合。记住：**令牌先行、语义命名、组件类复用**，主题就不会失控。
