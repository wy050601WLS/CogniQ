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
          <el-button size="large" @click="$router.push('/marketplace')">
            <el-icon><Grid /></el-icon>
            探索知识库
          </el-button>
        </div>
      </div>
      <div class="welcome-icon">📚</div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><Collection /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.kbCount }}</div>
          <div class="stat-label">知识库</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.docCount }}</div>
          <div class="stat-label">文档</div>
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
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Star /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.favCount }}</div>
          <div class="stat-label">收藏</div>
        </div>
      </div>
    </div>

    <!-- 推荐知识库 -->
    <div class="section">
      <div class="section-header">
        <h2>推荐知识库</h2>
        <el-button text @click="$router.push('/marketplace')">查看全部</el-button>
      </div>
      <div class="kb-grid">
        <div
          v-for="kb in knowledgeBases"
          :key="kb.id"
          class="kb-card"
          @click="handleViewKB(kb)"
        >
          <div class="kb-card-icon" :class="{ official: kb.is_official }">
            <el-icon><Collection /></el-icon>
          </div>
          <div class="kb-card-content">
            <h3>{{ kb.name }}</h3>
            <p>{{ kb.description || '暂无描述' }}</p>
            <div class="kb-card-meta">
              <span><el-icon><Document /></el-icon> {{ kb.doc_count }} 篇</span>
              <span><el-icon><User /></el-icon> {{ kb.copy_count }} 次复制</span>
            </div>
          </div>
          <el-tag v-if="kb.is_official" type="success" size="small">官方</el-tag>
        </div>
        <el-empty v-if="knowledgeBases.length === 0 && !loading" description="暂无推荐知识库" />
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
        <div class="action-card" @click="$router.push('/my-kb')">
          <el-icon class="action-icon blue"><Collection /></el-icon>
          <span>我的知识库</span>
        </div>
        <div class="action-card" @click="$router.push('/chat')">
          <el-icon class="action-icon green"><ChatDotRound /></el-icon>
          <span>智能问答</span>
        </div>
        <div class="action-card" @click="$router.push('/favorites')">
          <el-icon class="action-icon orange"><Star /></el-icon>
          <span>我的收藏</span>
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
  ChatDotRound, Grid, Collection, Document, User,
  Star, Clock, Loading
} from '@element-plus/icons-vue'
import { getMarketplace, getMyKnowledgeBases, getFavorites, getConversations } from '../api/knowledgeBase'

const router = useRouter()
const knowledgeBases = ref([])
const stats = ref({ kbCount: 0, docCount: 0, convCount: 0, favCount: 0 })
const loading = ref(true)

onMounted(async () => {
  try {
    const token = localStorage.getItem('token')
    
    // 并行加载数据
    const promises = [getMarketplace()]
    
    if (token) {
      promises.push(
        getMyKnowledgeBases().catch(() => ({ data: { items: [], total: 0 } })),
        getConversations().catch(() => ({ data: [] })),
        getFavorites().catch(() => ({ data: [] }))
      )
    }
    
    const results = await Promise.all(promises)
    
    // 处理知识库广场数据
    const marketplaceData = results[0].data
    knowledgeBases.value = (marketplaceData.items || []).slice(0, 4)
    
    // 处理用户数据
    if (token && results.length >= 4) {
      const myKBs = results[1].data?.items || []
      stats.value.kbCount = myKBs.length
      stats.value.docCount = myKBs.reduce((sum, kb) => sum + (kb.doc_count || 0), 0)
      stats.value.convCount = Array.isArray(results[2].data) ? results[2].data.length : 0
      stats.value.favCount = Array.isArray(results[3].data) ? results[3].data.length : 0
    }
  } catch (e) {
    console.error('加载首页数据失败:', e)
  } finally {
    loading.value = false
  }
})

function handleViewKB(kb) {
  const token = localStorage.getItem('token')
  if (token) {
    router.push(`/kb/${kb.id}`)
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  color: #fff;
}

.welcome-content h1 {
  margin: 0 0 12px;
  font-size: 28px;
  font-weight: 700;
}

.welcome-content p {
  margin: 0 0 24px;
  font-size: 16px;
  opacity: 0.9;
}

.welcome-actions {
  display: flex;
  gap: 12px;
}

.welcome-icon {
  font-size: 80px;
  opacity: 0.8;
}

/* 统计卡片 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
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
  font-size: 24px;
  color: #fff;
}

.stat-icon.blue { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); }
.stat-icon.green { background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); }
.stat-icon.purple { background: linear-gradient(135deg, #a855f7 0%, #9333ea 100%); }
.stat-icon.orange { background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); }

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
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h2, .section > h2 {
  margin: 0;
  font-size: 18px;
  color: #1e293b;
}

/* 加载状态 */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px;
  color: #94a3b8;
}

/* 知识库网格 */
.kb-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.kb-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  transition: all 0.2s;
}

.kb-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
}

.kb-card-icon {
  width: 52px;
  height: 52px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 26px;
  flex-shrink: 0;
}

.kb-card-icon.official {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
}

.kb-card-content {
  flex: 1;
  min-width: 0;
}

.kb-card-content h3 {
  margin: 0 0 4px;
  font-size: 16px;
  color: #1e293b;
}

.kb-card-content p {
  margin: 0 0 8px;
  font-size: 13px;
  color: #64748b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.kb-card-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #94a3b8;
}

.kb-card-meta span {
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
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  transition: all 0.2s;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
}

.action-icon {
  font-size: 32px;
}

.action-icon.blue { color: #3b82f6; }
.action-icon.green { color: #22c55e; }
.action-icon.orange { color: #f97316; }
.action-icon.purple { color: #a855f7; }

.action-card span {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}
</style>
