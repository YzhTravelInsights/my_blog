import { createRouter, createWebHashHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Article from '../views/Article.vue'
import About from '../views/About.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/article/:id', name: 'Article', component: Article, props: true },
  { path: '/about', name: 'About', component: About },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router
