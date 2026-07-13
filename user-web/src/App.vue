<template>
  <div class="app-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo">
          <div class="logo-icon">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <span class="logo-text">知识问答</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/" class="nav-item">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </router-link>
        <router-link to="/chat" class="nav-item">
          <el-icon><ChatDotRound /></el-icon>
          <span>智能问答</span>
        </router-link>
        <router-link to="/files" class="nav-item">
          <el-icon><Document /></el-icon>
          <span>我的文件</span>
        </router-link>
        <router-link to="/shared" class="nav-item">
          <el-icon><Grid /></el-icon>
          <span>知识广场</span>
        </router-link>
        <router-link to="/history" class="nav-item">
          <el-icon><Clock /></el-icon>
          <span>对话历史</span>
        </router-link>
        <router-link to="/help" class="nav-item">
          <el-icon><QuestionFilled /></el-icon>
          <span>帮助中心</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <template v-if="authStore.isLoggedIn">
          <div class="user-info" @click="$router.push('/profile')">
            <div class="avatar">{{ authStore.user?.nickname?.[0] || 'U' }}</div>
            <div class="user-detail">
              <div class="user-name">{{ authStore.user?.nickname || authStore.user?.username }}</div>
              <div class="user-email">{{ authStore.user?.email }}</div>
            </div>
          </div>
          <el-button text class="logout-btn" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
          </el-button>
        </template>
        <template v-else>
          <el-button type="primary" style="width: 100%" @click="$router.push('/login')">
            登录 / 注册
          </el-button>
        </template>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="main-wrapper">
      <!-- 顶部栏 -->
      <header class="topbar">
        <div class="topbar-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentTitle">{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="topbar-right">
          <el-button text circle @click="themeStore.toggle" :title="themeStore.isDark ? '切换到浅色模式' : '切换到深色模式'">
            <el-icon :size="18">
              <Sunny v-if="themeStore.isDark" />
              <Moon v-else />
            </el-icon>
          </el-button>
          <el-input
            v-model="globalSearch"
            placeholder="搜索文件..."
            prefix-icon="Search"
            clearable
            style="width: 240px"
            @keyup.enter="handleSearch"
            @clear="searchResults = []"
          />
          <!-- 搜索结果下拉 -->
          <div v-if="searchResults.length > 0" class="search-dropdown">
            <div
              v-for="kb in searchResults"
              :key="kb.id"
              class="search-item"
              @click="handleSearchResult(kb)"
            >
              <el-icon><Collection /></el-icon>
              <div class="search-item-info">
                <div class="search-item-name">{{ kb.name }}</div>
                <div class="search-item-desc">{{ kb.description || '暂无描述' }}</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- 页面内容 -->
      <main class="page-content" ref="pageContentRef">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>

      <!-- 返回顶部按钮 -->
      <transition name="fade">
        <div v-show="showBackTop" class="back-to-top" @click="scrollToTop">
          <el-icon><Top /></el-icon>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ChatDotRound, HomeFilled, Collection, Grid, Star,
  Clock, SwitchButton, Search, Top, QuestionFilled, Sunny, Moon
} from '@element-plus/icons-vue'
import { useAuthStore } from './stores/auth'
import { useThemeStore } from './stores/theme'
import { getSharedFiles } from './api/files'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()
const globalSearch = ref('')
const pageContentRef = ref(null)
const showBackTop = ref(false)
const searchResults = ref([])

const currentTitle = computed(() => {
  const titles = {
    '/chat': '智能问答',
    '/files': '我的文件',
    '/shared': '知识广场',
    '/history': '对话历史',
    '/profile': '个人中心',
  }
  return titles[route.path] || ''
})

async function handleSearch() {
  if (!globalSearch.value.trim()) {
    searchResults.value = []
    return
  }

  try {
    const { data } = await getMarketplace()
    const keyword = globalSearch.value.toLowerCase()
    searchResults.value = (data.items || []).filter(kb =>
      kb.name.toLowerCase().includes(keyword) ||
      (kb.description && kb.description.toLowerCase().includes(keyword))
    ).slice(0, 5)
  } catch (e) {
    console.error('搜索失败:', e)
  }
}

function handleSearchResult(kb) {
  searchResults.value = []
  globalSearch.value = ''
  if (authStore.isLoggedIn) {
    router.push(`/kb/${kb.id}`)
  } else {
    router.push('/login')
  }
}

function handleScroll() {
  if (pageContentRef.value) {
    showBackTop.value = pageContentRef.value.scrollTop > 300
  }
}

function scrollToTop() {
  if (pageContentRef.value) {
    pageContentRef.value.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

onMounted(() => {
  if (pageContentRef.value) {
    pageContentRef.value.addEventListener('scroll', handleScroll)
  }
  // 点击外部关闭搜索下拉
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  if (pageContentRef.value) {
    pageContentRef.value.removeEventListener('scroll', handleScroll)
  }
  document.removeEventListener('click', handleClickOutside)
})

function handleClickOutside(e) {
  // 如果点击的不是搜索区域，关闭下拉
  if (!e.target.closest('.topbar-right')) {
    searchResults.value = []
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  background: #f0f2f5;
}

/* 侧边栏 */
.sidebar {
  width: 220px;
  background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 10;
}

.sidebar-header {
  height: 64px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 20px;
}

.logo-text {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.sidebar-nav {
  flex: 1;
  padding: 12px 8px;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  color: #94a3b8;
  text-decoration: none;
  transition: all 0.2s;
  margin-bottom: 4px;
}

.nav-item:hover {
  background: rgba(255,255,255,0.1);
  color: #fff;
}

.nav-item.router-link-active {
  background: rgba(59, 130, 246, 0.3);
  color: #60a5fa;
}

.nav-item span {
  font-size: 14px;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.user-info:hover {
  background: rgba(255,255,255,0.1);
}

.avatar {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.user-detail {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-email {
  font-size: 12px;
  color: #64748b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.logout-btn {
  margin-top: 8px;
  width: 100%;
  color: #94a3b8;
}

.logout-btn:hover {
  color: #f87171;
}

/* 主内容区 */
.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.topbar {
  height: 64px;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
}

/* 搜索下拉 */
.search-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 320px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  z-index: 1000;
  margin-top: 8px;
  max-height: 400px;
  overflow-y: auto;
}

.search-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.search-item:hover {
  background: #f5f7fa;
}

.search-item:not(:last-child) {
  border-bottom: 1px solid #f0f0f0;
}

.search-item .el-icon {
  color: #3b82f6;
  font-size: 18px;
}

.search-item-info {
  flex: 1;
  min-width: 0;
}

.search-item-name {
  font-weight: 500;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.search-item-desc {
  font-size: 12px;
  color: #94a3b8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 2px;
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* 返回顶部按钮 */
.back-to-top {
  position: fixed;
  bottom: 40px;
  right: 40px;
  width: 44px;
  height: 44px;
  background: #3b82f6;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  transition: all 0.3s;
  z-index: 100;
}

.back-to-top:hover {
  background: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.5);
}

/* 页面过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
