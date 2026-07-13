import { createRouter, createWebHistory } from 'vue-router'
import { useAdminAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { hideLayout: true },
  },
  { path: '/', redirect: '/dashboard' },
  {
    path: '/dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/users',
    component: () => import('../views/Users.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/files',
    component: () => import('../views/Files.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/statistics',
    component: () => import('../views/Statistics.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/settings',
    component: () => import('../views/Settings.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAdminAuthStore()

  if (to.meta.requiresAuth) {
    if (!authStore.isLoggedIn || !authStore.isAdmin) {
      next('/login')
      return
    }
  }

  if (to.path === '/login' && authStore.isLoggedIn && authStore.isAdmin) {
    next('/dashboard')
    return
  }

  next()
})

export default router
