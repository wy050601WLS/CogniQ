<template>
  <!-- 登录页：不显示侧边栏布局 -->
  <div v-if="hideLayout">
    <router-view />
  </div>

  <!-- 其他页面：显示侧边栏布局 -->
  <div v-else class="admin-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed }">
      <div class="sidebar-header">
        <el-icon><Setting /></el-icon>
        <span v-if="!collapsed">管理后台</span>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/dashboard" class="nav-item">
          <el-icon><DataAnalysis /></el-icon>
          <span v-if="!collapsed">仪表盘</span>
        </router-link>
        <router-link to="/users" class="nav-item">
          <el-icon><User /></el-icon>
          <span v-if="!collapsed">用户管理</span>
        </router-link>
        <router-link to="/files" class="nav-item">
          <el-icon><Document /></el-icon>
          <span v-if="!collapsed">文件管理</span>
        </router-link>
        <router-link to="/statistics" class="nav-item">
          <el-icon><TrendCharts /></el-icon>
          <span v-if="!collapsed">数据统计</span>
        </router-link>
        <router-link to="/settings" class="nav-item">
          <el-icon><Setting /></el-icon>
          <span v-if="!collapsed">系统设置</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <el-button text @click="collapsed = !collapsed">
          <el-icon><Fold v-if="!collapsed" /><Expand v-else /></el-icon>
        </el-button>
      </div>
    </aside>

    <!-- 主内容 -->
    <div class="main-content">
      <header class="topbar">
        <h2>{{ currentTitle }}</h2>
        <div class="topbar-right">
          <el-button text circle @click="themeStore.toggle" :title="themeStore.isDark ? '切换到浅色模式' : '切换到深色模式'">
            <el-icon :size="18">
              <Sunny v-if="themeStore.isDark" />
              <Moon v-else />
            </el-icon>
          </el-button>
          <span class="admin-name">{{ authStore.username }}</span>
          <el-button text @click="handleLogout">退出登录</el-button>
        </div>
      </header>
      <main class="page-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Setting, DataAnalysis, User, Collection, Document, TrendCharts, Fold, Expand, Sunny, Moon } from '@element-plus/icons-vue'
import { useAdminAuthStore } from './stores/auth'
import { useThemeStore } from './stores/theme'

const route = useRoute()
const router = useRouter()
const authStore = useAdminAuthStore()
const themeStore = useThemeStore()
const collapsed = ref(false)

const hideLayout = computed(() => route.meta.hideLayout === true)

const currentTitle = computed(() => {
  const titles = {
    '/dashboard': '仪表盘',
    '/users': '用户管理',
    '/files': '文件管理',
    '/statistics': '数据统计',
    '/settings': '系统设置',
  }
  return titles[route.path] || '管理后台'
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
}

.sidebar {
  width: 220px;
  background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  height: 64px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  white-space: nowrap;
  overflow: hidden;
}

.sidebar-nav {
  flex: 1;
  padding: 12px 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  color: #94a3b8;
  text-decoration: none;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
}

.nav-item:hover {
  background: rgba(255,255,255,0.1);
  color: #fff;
}

.nav-item.router-link-active {
  background: rgba(59, 130, 246, 0.3);
  color: #60a5fa;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.sidebar-footer .el-button {
  color: #94a3b8;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.topbar {
  height: 64px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.topbar h2 {
  margin: 0;
  font-size: 18px;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.admin-name {
  color: #606266;
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}
</style>
