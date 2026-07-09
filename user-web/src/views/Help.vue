<template>
  <div class="help-page">
    <h1>帮助中心</h1>

    <!-- 搜索框 -->
    <div class="search-section">
      <el-input
        v-model="searchQuery"
        placeholder="搜索问题或功能..."
        prefix-icon="Search"
        clearable
        size="large"
        @keyup.enter="handleSearch"
      />
    </div>

    <!-- 搜索结果 -->
    <div v-if="searchResults.length > 0" class="search-results">
      <h2>搜索结果（{{ searchResults.length }} 条）</h2>
      <div
        v-for="item in searchResults"
        :key="item.id"
        class="result-item"
        @click="showDetail(item)"
      >
        <div class="result-category">{{ item.category }}</div>
        <div class="result-title">{{ item.title }}</div>
        <div class="result-tags">
          <el-tag v-for="tag in item.tags" :key="tag" size="small" type="info">{{ tag }}</el-tag>
        </div>
      </div>
      <el-button text @click="searchResults = []">清除搜索</el-button>
    </div>

    <!-- 分类列表 -->
    <div v-else class="categories">
      <div
        v-for="category in categories"
        :key="category.id"
        class="category-card"
        @click="selectedCategory = category.id"
      >
        <el-icon :size="32">
          <component :is="category.icon" />
        </el-icon>
        <h3>{{ category.title }}</h3>
      </div>
    </div>

    <!-- 分类详情 -->
    <div v-if="selectedCategory && !searchQuery" class="category-detail">
      <div class="detail-header">
        <el-button text @click="selectedCategory = null">
          <el-icon><ArrowLeft /></el-icon> 返回
        </el-button>
        <h2>{{ currentCategory?.title }}</h2>
      </div>

      <div class="items-list">
        <div
          v-for="item in currentCategory?.items"
          :key="item.id"
          class="item-card"
          @click="showDetail(item)"
        >
          <h3>{{ item.title }}</h3>
          <p>{{ item.content.substring(0, 100).replace(/[#*\n]/g, ' ').trim() }}...</p>
          <div class="item-tags">
            <el-tag v-for="tag in item.tags" :key="tag" size="small">{{ tag }}</el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="currentItem?.title"
      width="700px"
      top="8vh"
    >
      <div v-if="currentItem" class="detail-content" v-html="renderMarkdown(currentItem.content)" />
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Setting, Collection, ChatDotRound, Star, User,
  Warning, ArrowLeft, Search
} from '@element-plus/icons-vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import api from '../api'

const categories = ref([])
const selectedCategory = ref(null)
const searchQuery = ref('')
const searchResults = ref([])
const showDetailDialog = ref(false)
const currentItem = ref(null)

const categoryData = ref({})

const currentCategory = computed(() => {
  return categoryData.value[selectedCategory.value] || null
})

onMounted(async () => {
  try {
    const { data } = await api.get('/help')
    // 添加图标映射
    const iconMap = {
      'getting-started': Setting,
      'knowledge-base': Collection,
      'chat': ChatDotRound,
      'favorites': Star,
      'profile': User,
      'troubleshooting': Warning,
      'admin': Setting,
    }
    categories.value = data.map(cat => ({
      ...cat,
      icon: iconMap[cat.id] || Setting
    }))
  } catch (e) {
    console.error('加载帮助内容失败:', e)
  }
})

async function showDetail(item) {
  try {
    const { data } = await api.get(`/help/item/${item.id}`)
    currentItem.value = data
    showDetailDialog.value = true
  } catch (e) {
    console.error('加载详情失败:', e)
  }
}

async function handleSearch() {
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    return
  }

  try {
    const { data } = await api.get(`/help/search?q=${encodeURIComponent(searchQuery.value)}`)
    searchResults.value = data.results || []
  } catch (e) {
    console.error('搜索失败:', e)
  }
}

function renderMarkdown(content) {
  return DOMPurify.sanitize(marked.parse(content || ''))
}
</script>

<style scoped>
.help-page {
  max-width: 1000px;
  margin: 0 auto;
}

.help-page h1 {
  font-size: 28px;
  margin-bottom: 24px;
}

.search-section {
  margin-bottom: 32px;
}

/* 分类卡片 */
.categories {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.category-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e4e7ed;
}

.category-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}

.category-card .el-icon {
  color: #409eff;
  margin-bottom: 12px;
}

.category-card h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

/* 分类详情 */
.detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.detail-header h2 {
  margin: 0;
  font-size: 22px;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.item-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e4e7ed;
}

.item-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.item-card h3 {
  margin: 0 0 8px;
  font-size: 16px;
  color: #303133;
}

.item-card p {
  margin: 0 0 12px;
  font-size: 14px;
  color: #909399;
  line-height: 1.5;
}

.item-tags {
  display: flex;
  gap: 8px;
}

/* 搜索结果 */
.search-results {
  margin-bottom: 24px;
}

.search-results h2 {
  font-size: 18px;
  margin-bottom: 16px;
  color: #606266;
}

.result-item {
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  border: 1px solid #e4e7ed;
  transition: all 0.2s;
}

.result-item:hover {
  border-color: #409eff;
}

.result-category {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.result-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
}

.result-tags {
  display: flex;
  gap: 8px;
}

/* 详情弹窗 */
.detail-content {
  line-height: 1.8;
  color: #303133;
}

.detail-content :deep(h3) {
  margin: 20px 0 12px;
  font-size: 18px;
}

.detail-content :deep(ul), .detail-content :deep(ol) {
  padding-left: 24px;
}

.detail-content :deep(li) {
  margin-bottom: 8px;
}

.detail-content :deep(code) {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.detail-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
}

.detail-content :deep(th), .detail-content :deep(td) {
  border: 1px solid #e4e7ed;
  padding: 8px 12px;
  text-align: left;
}

.detail-content :deep(th) {
  background: #f5f7fa;
}
</style>
