<template>
  <div class="favorites-page">
    <h1>我的收藏</h1>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <!-- 收藏列表 -->
    <div v-else class="kb-grid">
      <div
        v-for="fav in favorites"
        :key="fav.id"
        class="kb-card"
        @click="handleViewKB(fav.knowledge_base)"
      >
        <div class="kb-icon"><el-icon><Star /></el-icon></div>
        <div class="kb-content">
          <h3>{{ fav.knowledge_base?.name }}</h3>
          <p>{{ fav.knowledge_base?.description || '暂无描述' }}</p>
        </div>
        <div class="kb-footer">
          <span><el-icon><Document /></el-icon> {{ fav.knowledge_base?.doc_count || 0 }} 篇文档</span>
          <el-button text type="danger" size="small" @click.stop="removeFav(fav)">
            取消收藏
          </el-button>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && favorites.length === 0" class="empty-state">
        <el-empty description="暂无收藏">
          <el-button type="primary" @click="$router.push('/marketplace')">去发现知识库</el-button>
        </el-empty>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Star, Document, Loading } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getFavorites, removeFavorite } from '../api/knowledgeBase'

const router = useRouter()
const favorites = ref([])
const loading = ref(true)

onMounted(async () => {
  await loadData()
})

async function loadData() {
  loading.value = true
  try {
    const { data } = await getFavorites()
    favorites.value = data || []
  } catch (e) {
    console.error('加载收藏失败:', e)
    ElMessage.error('加载收藏列表失败')
  } finally {
    loading.value = false
  }
}

function handleViewKB(kb) {
  if (kb?.id) {
    router.push(`/kb/${kb.id}`)
  }
}

async function removeFav(fav) {
  try {
    await ElMessageBox.confirm('确定取消收藏？', '确认')
    await removeFavorite(fav.id)
    favorites.value = favorites.value.filter(f => f.id !== fav.id)
    ElMessage.success('已取消收藏')
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('取消收藏失败')
    }
  }
}
</script>

<style scoped>
.favorites-page h1 {
  margin: 0 0 24px;
  font-size: 24px;
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
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.kb-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e4e7ed;
  cursor: pointer;
  transition: all 0.2s;
}

.kb-card:hover {
  border-color: #e6a23c;
  box-shadow: 0 4px 12px rgba(230, 162, 60, 0.15);
  transform: translateY(-2px);
}

.kb-icon {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #e6a23c 0%, #d4910a 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 22px;
  margin-bottom: 12px;
}

.kb-content {
  flex: 1;
}

.kb-card h3 {
  margin: 0 0 8px;
  font-size: 16px;
}

.kb-card p {
  margin: 0 0 12px;
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
}

.kb-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #94a3b8;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.kb-footer span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.empty-state {
  grid-column: 1 / -1;
}
</style>
