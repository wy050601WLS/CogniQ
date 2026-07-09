<template>
  <div class="marketplace-page">
    <h1>知识库广场</h1>
    <p>探索公开知识库，复制到自己的账号</p>

    <!-- 搜索和筛选 -->
    <div class="filter-bar">
      <el-input
        v-model="searchText"
        placeholder="搜索知识库..."
        prefix-icon="Search"
        clearable
        style="width: 300px"
      />
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <!-- 知识库列表 -->
    <div v-else class="kb-grid">
      <div
        v-for="kb in filteredKBs"
        :key="kb.id"
        class="kb-card"
        @click="handleViewKB(kb)"
      >
        <div class="kb-icon" :class="{ official: kb.is_official }">
          <el-icon><Collection /></el-icon>
        </div>
        <div class="kb-card-body">
          <h3>{{ kb.name }}</h3>
          <p>{{ kb.description || '暂无描述' }}</p>
          <div class="kb-meta">
            <span><el-icon><Document /></el-icon> {{ kb.doc_count }} 篇文档</span>
            <span><el-icon><CopyDocument /></el-icon> {{ kb.copy_count }} 次复制</span>
          </div>
        </div>
        <div class="kb-actions">
          <el-tag v-if="kb.is_official" type="success" size="small">官方</el-tag>
          <el-button type="primary" size="small" @click.stop="handleCopy(kb)" :loading="copyingId === kb.id">
            复制
          </el-button>
        </div>
      </div>
      <el-empty v-if="filteredKBs.length === 0 && !loading" description="暂无公开知识库" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Collection, Document, CopyDocument, Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getMarketplace, copyKnowledgeBase } from '../api/knowledgeBase'

const router = useRouter()
const knowledgeBases = ref([])
const loading = ref(true)
const copyingId = ref(null)
const searchText = ref('')

const filteredKBs = computed(() => {
  if (!searchText.value) return knowledgeBases.value
  const keyword = searchText.value.toLowerCase()
  return knowledgeBases.value.filter(kb =>
    kb.name.toLowerCase().includes(keyword) ||
    (kb.description && kb.description.toLowerCase().includes(keyword))
  )
})

onMounted(async () => {
  try {
    const { data } = await getMarketplace()
    knowledgeBases.value = data.items || []
  } catch (e) {
    console.error('加载知识库失败:', e)
    ElMessage.error('加载知识库失败')
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

async function handleCopy(kb) {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  copyingId.value = kb.id
  try {
    await copyKnowledgeBase(kb.id)
    ElMessage.success(`已复制「${kb.name}」`)
    // 更新复制次数（创建新数组触发响应式更新）
    knowledgeBases.value = knowledgeBases.value.map(item =>
      item.id === kb.id ? { ...item, copy_count: (item.copy_count || 0) + 1 } : item
    )
  } catch (e) {
    ElMessage.error('复制失败，请重试')
  } finally {
    copyingId.value = null
  }
}
</script>

<style scoped>
.marketplace-page h1 {
  margin: 0 0 8px;
  font-size: 24px;
}

.marketplace-page > p {
  color: #909399;
  margin: 0 0 24px;
}

.filter-bar {
  margin-bottom: 24px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 80px 0;
  color: #94a3b8;
}

.kb-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.kb-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e4e7ed;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
}

.kb-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.kb-icon {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #409eff 0%, #337ecc 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 22px;
  margin-bottom: 12px;
}

.kb-icon.official {
  background: linear-gradient(135deg, #67c23a 0%, #529b2e 100%);
}

.kb-card-body {
  flex: 1;
}

.kb-card-body h3 {
  margin: 0 0 8px;
  font-size: 16px;
}

.kb-card-body p {
  margin: 0 0 12px;
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
}

.kb-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #94a3b8;
}

.kb-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.kb-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}
</style>
