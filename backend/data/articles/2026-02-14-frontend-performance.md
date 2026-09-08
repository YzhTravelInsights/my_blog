---
title: "前端性能优化清单：从加载到交互的全链路"
date: 2026-02-14
category: 前端
tags: ["性能优化", "Vite", "构建"]
summary: "一份可直接照着做的前端性能优化清单：拆包、懒加载、图片、缓存，逐条讲清原理与收益。"
---

## 引言

用户可感知的「快」，由两个指标决定：**加载快**（LCP）和**交互快**（INP）。这份清单围绕这两个指标展开。

## 构建层面

### 代码分包

用 Vite 的 `manualChunks` 把体积大的依赖拆开，避免首屏加载巨型 bundle：

```js
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          three: ['three'],
        },
      },
    },
  },
})
```

### 路由懒加载

把每个页面拆成独立的 chunk，访问到了才加载：

```js
const Home = () => import('../views/Home.vue')
```

## 运行时层面

### 图片优化

- 合理尺寸，别用 2048px 的图显示 96px 的头像
- 使用现代格式（WebP/AVIF）
- 关键图 `loading="lazy"` + `decoding="async"`

### 减少主线程负担

- 长列表虚拟滚动
- 动画优先用 transform/opacity（不触发重排）
- 节流/防抖高频事件

## 缓存策略

- 静态资源加内容哈希，长久缓存
- 依赖包与业务代码分离，依赖不变就命中缓存

## 小结

性能优化不是玄学，是一份**可以照着打的清单**。先测，再改，最后复测，用数据说话。
