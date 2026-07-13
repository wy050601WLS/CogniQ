<template>
  <div class="home-page">
    <!-- 欢迎卡片 -->
    <div class="welcome-card">
      <div class="welcome-content">
        <h1>欢迎使用知识问答系统</h1>
        <p>基于 RAG 技术的智能问答平台，让知识触手可及</p>
        <div class="welcome-actions">
          <el-button type="primary" size="large" @click="$router.push('/chat')">
            <el-icon><ChatDotRound /></el-icon>
            开始问答
          </el-button>
          <el-button size="large" @click="$router.push('/files')">
            <el-icon><Upload /></el-icon>
            上传文件
          </el-button>
        </div>
      </div>
      <div class="welcome-icon">📚</div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.fileCount }}</div>
          <div class="stat-label">文件</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><ChatDotRound /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.convCount }}</div>
          <div class="stat-label">对话</div>
        </div>
      </div>
    </div>

    <!-- 推荐文件 -->
    <div class="section">
      <div class="section-header">
        <h2>推荐文件</h2>
        <el-button text @click="$router.push('/shared')">查看全部</el-button>
      </div>
      <div class="file-grid">
        <div
          v-for="file in sharedFiles"
          :key="file.id"
          class="file-card"
          @click="handleViewFile(file)"
        >
          <div class="file-icon" :class="getFileTypeClass(file.file_type)">
            <el-icon><Document /></el-icon>
          </div>
          <div class="file-card-content">
            <h3>{{ file.filename }}</h3>
            <p>{{ file.description || '暂无描述' }}</p>
            <div class="file-card-meta">
              <span><el-icon><View /></el-icon> {{ file.view_count }} 次查看</span>
              <span><el-icon><CopyDocument /></el-icon> {{ file.copy_count }} 次复制</span>
            </div>
          </div>
        </div>
        <el-empty v-if="sharedFiles.length === 0 && !loading" description="暂无推荐文件" />
      </div>
      <div v-if="loading" class="loading-state">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="section">
      <h2>快捷操作</h2>
      <div class="action-grid">
        <div class="action-card" @click="$router.push('/files')">
          <el-icon class="action-icon blue"><Document /></el-icon>
          <span>我的文件</span>
        </div>
        <div class="action-card" @click="$router.push('/chat')">
          <el-icon class="action-icon green"><ChatDotRound /></el-icon>
          <span>智能问答</span>
        </div>
        <div class="action-card" @click="$router.push('/shared')">
          <el-icon class="action-icon orange"><Grid /></el-icon>
          <span>知识广场</span>
        </div>
        <div class="action-card" @click="$router.push('/history')">
          <el-icon class="action-icon purple"><Clock /></el-icon>
          <span>对话历史</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  ChatDotRound, Grid, Document, User,
  Clock, Loading, Upload, View, CopyDocument
} from '@element-plus/icons-vue'
import { getSharedFiles } from '../api/files'
import { getConversations } from '../api/files'

const router = useRouter()
const sharedFiles = ref([])
const stats = ref({ fileCount: 0, convCount: 0 })
const loading = ref(true)

onMounted(async () => {
  try {
    const token = localStorage.getItem('token')

    // 加载公开文件
    const filesRes = await getSharedFiles().catch(() => ({ data: [] }))
    sharedFiles.value = (filesRes.data || []).slice(0, 4)

    // 加载对话统计
    if (token) {
      const convRes = await getConversations().catch(() => ({ data: [] }))
      stats.value.convCount = Array.isArray(convRes.data) ? convRes.data.length : 0
    }
  } catch (e) {
    console.error('加载首页数据失败:', e)
  } finally {
    loading.value = false
  }
})

function getFileTypeClass(type) {
  const classes = {
    pdf: 'type-pdf',
    docx: 'type-word',
    doc: 'type-word',
    md: 'type-md',
    txt: 'type-txt',
    html: 'type-html'
  }
  return classes[type] || ''
}

function handleViewFile(file) {
  const token = localStorage.getItem('token')
  if (token) {
    router.push(`/files/${file.id}`)
  } else {
    router.push('/login')
  }
}
</script>

<style scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
}

/* 欢迎卡片 */
.welcome-card {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 16px;
  padding: 40px;
  margin-bottom: 32px;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-content h1 {
  margin: 0 0 12px;
  font-size: 28px;
}

.welcome-content p {
  margin: 0 0 24px;
  opacity: 0.9;
  font-size: 16px;
}

.welcome-actions {
  display: flex;
  gap: 12px;
}

.welcome-icon {
  font-size: 80px;
}

/* 统计卡片 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-icon.blue { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.stat-icon.green { background: linear-gradient(135deg, #22c55e, #16a34a); }
.stat-icon.purple { background: linear-gradient(135deg, #a855f7, #9333ea); }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 2px;
}

/* 区块 */
.section {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h2 {
  margin: 0;
  font-size: 20px;
}

/* 文件网格 */
.file-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.file-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.2s;
}

.file-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

.file-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin-bottom: 12px;
  background: #f1f5f9;
  color: #64748b;
}

.file-icon.type-pdf { background: #fee2e2; color: #ef4444; }
.file-icon.type-word { background: #dbeafe; color: #3b82f6; }
.file-icon.type-md { background: #dcfce7; color: #22c55e; }

.file-card-content h3 {
  margin: 0 0 4px;
  font-size: 15px;
  color: #1e293b;
}

.file-card-content p {
  margin: 0 0 8px;
  font-size: 13px;
  color: #64748b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-card-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #94a3b8;
}

.file-card-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 快捷操作 */
.action-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.action-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e2e8f0;
}

.action-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.action-icon {
  font-size: 28px;
  margin-bottom: 8px;
}

.action-icon.blue { color: #3b82f6; }
.action-icon.green { color: #22c55e; }
.action-icon.orange { color: #f97316; }
.action-icon.purple { color: #a855f7; }

.action-card span {
  font-size: 14px;
  color: #1e293b;
}

/* 加载状态 */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px 0;
  color: #94a3b8;
}
</style>
