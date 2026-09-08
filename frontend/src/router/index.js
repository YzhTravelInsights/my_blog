import { createRouter, createWebHashHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Article from '../views/Article.vue'
import About from '../views/About.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/article/:id', name: 'Article', component: Article, props: true },
  { path: '/about', name: 'About', component: About },
  // 图库懒加载，避免主包变大、也让路由测试无需 stub 该视图
  { path: '/gallery', name: 'Gallery', component: () => import('../views/Gallery.vue') },
  // 主人私聊 / 管理后台 / 发布文章（懒加载；均需 OWNER_SECRET 认证）
  { path: '/chat', name: 'OwnerChat', component: () => import('../views/OwnerChat.vue') },
  { path: '/admin', name: 'Admin', component: () => import('../views/Admin.vue') },
  { path: '/write', name: 'Write', component: () => import('../views/Write.vue') },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router
