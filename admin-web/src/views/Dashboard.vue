<template>
  <div class="dashboard">
    <!-- 欢迎信息 -->
    <div class="welcome-section">
      <div class="welcome-text">
        <h2>欢迎回来，管理员</h2>
        <p>这是知识问答系统的管理后台</p>
      </div>
      <div class="welcome-time">{{ currentTime }}</div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card blue" @click="$router.push('/users')">
        <div class="stat-icon">
          <el-icon :size="28"><User /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.userCount }}</div>
          <div class="stat-label">用户总数</div>
        </div>
      </div>
      <div class="stat-card green" @click="$router.push('/files')">
        <div class="stat-icon">
          <el-icon :size="28"><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.fileCount }}</div>
          <div class="stat-label">文件总数</div>
        </div>
      </div>
      <div class="stat-card orange">
        <div class="stat-icon">
          <el-icon :size="28"><ChatDotRound /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.convCount }}</div>
          <div class="stat-label">对话总数</div>
        </div>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="quick-actions">
      <h3>快捷操作</h3>
      <div class="action-grid">
        <div class="action-card" @click="$router.push('/users')">
          <el-icon class="action-icon blue"><User /></el-icon>
          <span>用户管理</span>
        </div>
        <div class="action-card" @click="$router.push('/files')">
          <el-icon class="action-icon green"><Document /></el-icon>
          <span>文件管理</span>
        </div>
        <div class="action-card" @click="$router.push('/settings')">
          <el-icon class="action-icon orange"><Setting /></el-icon>
          <span>系统设置</span>
        </div>
      </div>
    </div>

    <!-- 系统信息 -->
    <div class="info-section">
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>系统信息</span>
          </div>
        </template>
        <div class="info-list">
          <div class="info-item">
            <span class="info-label">系统版本</span>
            <span class="info-value">1.0.0</span>
          </div>
          <div class="info-item">
            <span class="info-label">后端框架</span>
            <span class="info-value">FastAPI</span>
          </div>
          <div class="info-item">
            <span class="info-label">前端框架</span>
            <span class="info-value">Vue 3 + Element Plus</span>
          </div>
          <div class="info-item">
            <span class="info-label">数据库</span>
            <span class="info-value">MySQL</span>
          </div>
          <div class="info-item">
            <span class="info-label">向量库</span>
            <span class="info-value">ChromaDB</span>
          </div>
          <div class="info-item">
            <span class="info-label">LLM</span>
            <span class="info-value">Ollama (qwen2:7b)</span>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { User, Collection, Document, ChatDotRound, Setting } from '@element-plus/icons-vue'
import { getOverviewStats } from '../api'

const stats = ref({
  userCount: 0,
  kbCount: 0,
  docCount: 0,
  convCount: 0,
})

const currentTime = ref('')
let timer = null

function updateTime() {
  const now = new Date()
  const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }
  currentTime.value = now.toLocaleDateString('zh-CN', options)
}

onMounted(async () => {
  updateTime()
  timer = setInterval(updateTime, 60000)

  try {
    const { data } = await getOverviewStats()
    stats.value = {
      userCount: data.user_count || 0,
      fileCount: data.file_count || 0,
      convCount: data.conversation_count || 0,
    }
  } catch (e) {
    console.error('加载统计失败', e)
  }
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
}

/* 欢迎区域 */
.welcome-section {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 24px;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-text h2 {
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: 600;
}

.welcome-text p {
  margin: 0;
  opacity: 0.9;
}

.welcome-time {
  font-size: 14px;
  opacity: 0.8;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-card.blue .stat-icon { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.stat-card.green .stat-icon { background: linear-gradient(135deg, #22c55e, #16a34a); }
.stat-card.purple .stat-icon { background: linear-gradient(135deg, #a855f7, #9333ea); }
.stat-card.orange .stat-icon { background: linear-gradient(135deg, #f97316, #ea580c); }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
}

/* 快捷操作 */
.quick-actions {
  margin-bottom: 24px;
}

.quick-actions h3 {
  margin: 0 0 16px;
  font-size: 16px;
  color: #1e293b;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.action-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.action-icon {
  font-size: 32px;
}

.action-icon.blue { color: #3b82f6; }
.action-icon.green { color: #22c55e; }
.action-icon.purple { color: #a855f7; }
.action-icon.orange { color: #f97316; }

.action-card span {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}

/* 系统信息 */
.info-section {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.info-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.info-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
}

.info-label {
  font-size: 12px;
  color: #94a3b8;
}

.info-value {
  font-size: 14px;
  color: #1e293b;
  font-weight: 500;
}
</style>
