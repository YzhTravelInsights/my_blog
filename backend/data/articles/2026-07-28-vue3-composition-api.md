---
title: "Vue 3 组合式 API 入门：从 Options 到 Setup"
date: 2026-07-28
category: 前端
tags: ["Vue3", "组合式API", "响应式"]
summary: "介绍 Vue 3 组合式 API 的基本用法，对比 Options API，并给出实际迁移案例。"
---

## 从 Options 说起

很多老项目都还是 `data` / `methods` / `computed` 的写法。组件逻辑一多，同一功能的代码会被拆散到各个选项中。

## Setup 带来什么

组合式 API 允许我们把相关逻辑聚在一起，用函数组织，而不是用选项组织。

```js
import { ref, computed } from 'vue'

export default {
  setup() {
    const count = ref(0)
    const doubled = computed(() => count.value * 2)
    const inc = () => count.value++
    return { count, doubled, inc }
  },
}
```

### 响应式 API 速览

- `ref`：包裹基本类型，`.value` 访问
- `reactive`：包裹对象
- `computed`：派生状态
- `watch`：侦听变化

## 迁移建议

不必一次性推翻所有组件。优先在**新功能**里使用组合式 API，把公共逻辑抽成 `useXxx()` 组合函数，收益最明显。

## 小结

组合式 API 不是银弹，但它确实让复杂组件更容易维护。多写、多用，自然会体会到它的好。
