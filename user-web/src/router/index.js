import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'

function lazyLoad(view) {
  return () => import(`../views/${view}.vue`).catch((err) => {
    console.error('页面加载失败:', view, err)
    return import('../views/NotFound.vue')
  })
}

const routes = [
  {
    path: '/',
    name: 'Home',
    component: lazyLoad('Home'),
    meta: { title: '首页' },
  },
  {
    path: '/login',
    name: 'Login',
    component: lazyLoad('Login'),
    meta: { title: '登录' },
  },
  {
    path: '/register',
    name: 'Register',
    component: lazyLoad('Register'),
    meta: { title: '注册' },
  },
  {
    path: '/chat',
    name: 'Chat',
    component: lazyLoad('Chat'),
    meta: { requiresAuth: true, title: '智能问答' },
  },
  {
    path: '/files',
    name: 'Files',
    component: lazyLoad('Files'),
    meta: { requiresAuth: true, title: '我的文件' },
  },
  {
    path: '/files/:id',
    name: 'FileDetail',
    component: lazyLoad('FileDetail'),
    meta: { requiresAuth: true, title: '文件详情' },
  },
  {
    path: '/history',
    name: 'History',
    component: lazyLoad('History'),
    meta: { requiresAuth: true, title: '对话历史' },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: lazyLoad('Profile'),
    meta: { requiresAuth: true, title: '个人中心' },
  },
  {
    path: '/shared',
    name: 'Shared',
    component: lazyLoad('Shared'),
    meta: { title: '知识广场' },
  },
  {
    path: '/help',
    name: 'Help',
    component: lazyLoad('Help'),
    meta: { title: '帮助中心' },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: lazyLoad('NotFound'),
    meta: { title: '页面未找到' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    return { top: 0 }
  },
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    ElMessage.info('请先登录后再使用该功能')
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    next('/')
  } else {
    next()
  }
})

// 动态标题
router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} - 知识问答系统` : '知识问答系统'
})

// 懒加载失败重试
router.onError((error) => {
  if (/Loading chunk \d+ failed/i.test(error.message)) {
    ElMessage.error('页面加载失败，正在刷新...')
    window.location.reload()
  }
})

export default router
