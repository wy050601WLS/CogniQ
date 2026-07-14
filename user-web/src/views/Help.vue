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
        @input="handleSearchInput"
        @keyup.enter="handleSearch"
        @clear="clearSearch"
      />
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <!-- 搜索结果 -->
    <div v-else-if="searchResults.length > 0" class="search-results">
      <div class="search-header">
        <h2>搜索结果（{{ searchResults.length }} 条）</h2>
        <el-button text @click="clearSearch">
          <el-icon><Close /></el-icon> 清除搜索
        </el-button>
      </div>
      <div
        v-for="item in searchResults"
        :key="item.id"
        class="result-item"
        @click="showDetail(item)"
      >
        <div class="result-category">{{ item.category }}</div>
        <div class="result-title">{{ item.title }}</div>
        <div v-if="item.snippet" class="result-snippet">{{ item.snippet }}</div>
        <div class="result-tags">
          <el-tag v-for="tag in item.tags" :key="tag" size="small" type="info">{{ tag }}</el-tag>
        </div>
      </div>
    </div>

    <!-- 搜索无结果 -->
    <div v-else-if="searchQuery && hasSearched" class="empty-search">
      <el-empty description="未找到相关内容，试试其他关键词">
        <el-button @click="clearSearch">返回分类</el-button>
      </el-empty>
    </div>

    <!-- 分类列表 -->
    <div v-else class="categories">
      <div
        v-for="category in categories"
        :key="category.id"
        class="category-card"
        @click="selectCategory(category.id)"
      >
        <div class="category-icon">
          <el-icon :size="32">
            <component :is="category.icon" />
          </el-icon>
        </div>
        <h3>{{ category.title }}</h3>
        <div class="category-count">{{ category.count || 0 }} 篇文章</div>
      </div>
    </div>

    <!-- 分类详情 -->
    <transition name="slide-fade">
      <div v-if="selectedCategory && !searchQuery" class="category-detail">
        <div class="detail-header">
          <el-button text @click="selectedCategory = null">
            <el-icon><ArrowLeft /></el-icon> 返回全部分类
          </el-button>
          <h2>{{ currentCategory?.title }}</h2>
        </div>

        <!-- 分类详情加载中 -->
        <div v-if="categoryLoading" class="category-loading">
          <el-icon class="is-loading" :size="24"><Loading /></el-icon>
          <span>加载中...</span>
        </div>

        <div v-else class="items-list">
          <div
            v-for="item in currentCategory?.items"
            :key="item.id"
            class="item-card"
            @click="showDetail(item)"
          >
            <div class="item-card-header">
              <h3>{{ item.title }}</h3>
              <el-icon class="item-arrow"><ArrowRight /></el-icon>
            </div>
            <p>{{ getPreview(item.content) }}</p>
            <div class="item-tags">
              <el-tag v-for="tag in item.tags" :key="tag" size="small">{{ tag }}</el-tag>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="currentItem?.title"
      width="700px"
      top="8vh"
      class="help-detail-dialog"
    >
      <div v-if="currentItem" class="detail-content" v-html="renderMarkdown(currentItem.content)" />
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Setting, Collection, ChatDotRound, Star, User,
  Warning, ArrowLeft, ArrowRight, Search, Close, Loading
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
const loading = ref(true)
const categoryLoading = ref(false)
const hasSearched = ref(false)

const categoryData = ref({})

const currentCategory = computed(() => {
  return categoryData.value[selectedCategory.value] || null
})

let searchTimer = null

onUnmounted(() => {
  if (searchTimer) clearTimeout(searchTimer)
})

function handleSearchInput() {
  if (searchTimer) clearTimeout(searchTimer)
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    hasSearched.value = false
    return
  }
  searchTimer = setTimeout(() => {
    handleSearch()
  }, 300)
}

function clearSearch() {
  searchQuery.value = ''
  searchResults.value = []
  hasSearched.value = false
}

async function selectCategory(categoryId) {
  selectedCategory.value = categoryId
  if (!categoryData.value[categoryId]) {
    categoryLoading.value = true
    try {
      const { data } = await api.get(`/help/${categoryId}`)
      categoryData.value = { ...categoryData.value, [categoryId]: data }
    } catch (e) {
      ElMessage.error('加载分类详情失败')
    } finally {
      categoryLoading.value = false
    }
  }
}

function getPreview(content) {
  if (!content) return '暂无内容'
  return content
    .replace(/[#*\n|`]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .substring(0, 80) + '...'
}

onMounted(async () => {
  try {
    const { data } = await api.get('/help')
    const iconMap = {
      'getting-started': Setting,
      'chat': ChatDotRound,
      'profile': User,
      'troubleshooting': Warning,
      'admin': Setting,
    }
    categories.value = data.map(cat => ({
      ...cat,
      icon: iconMap[cat.id] || Setting
    }))
  } catch (e) {
    ElMessage.error('加载帮助内容失败，请刷新页面重试')
  } finally {
    loading.value = false
  }
})

async function showDetail(item) {
  try {
    const { data } = await api.get(`/help/item/${item.id}`)
    currentItem.value = data
    showDetailDialog.value = true
  } catch (e) {
    ElMessage.error('加载详情失败')
  }
}

async function handleSearch() {
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    hasSearched.value = false
    return
  }

  try {
    const { data } = await api.get(`/help/search?q=${encodeURIComponent(searchQuery.value)}`)
    searchResults.value = data.results || []
    hasSearched.value = true
  } catch (e) {
    ElMessage.error('搜索失败，请重试')
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

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 80px 0;
  color: #94a3b8;
}

/* 分类卡片 */
.categories {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
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

.category-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #409eff 0%, #337ecc 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  color: #fff;
}

.category-card h3 {
  margin: 0 0 4px;
  font-size: 16px;
  color: #303133;
}

.category-count {
  font-size: 12px;
  color: #909399;
}

/* 分类详情 */
.category-detail {
  margin-top: 32px;
}

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

.category-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px 0;
  color: #94a3b8;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
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

.item-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.item-card-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.item-arrow {
  color: #c0c4cc;
  transition: transform 0.2s;
}

.item-card:hover .item-arrow {
  color: #409eff;
  transform: translateX(4px);
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

.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.search-header h2 {
  font-size: 18px;
  margin: 0;
  color: #606266;
}

.empty-search {
  padding: 60px 0;
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
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
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

.result-snippet {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
  line-height: 1.5;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.result-tags {
  display: flex;
  gap: 8px;
}

/* 详情弹窗 */
:deep(.help-detail-dialog .el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
  padding: 20px 24px;
}

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

/* 过渡动画 */
.slide-fade-enter-active {
  transition: all 0.3s ease;
}

.slide-fade-leave-active {
  transition: all 0.2s ease;
}

.slide-fade-enter-from {
  transform: translateY(20px);
  opacity: 0;
}

.slide-fade-leave-to {
  opacity: 0;
}

/* 深色模式 */
.dark .category-card {
  background: #1e293b;
  border-color: #334155;
}

.dark .category-card h3 {
  color: #e2e8f0;
}

.dark .category-count {
  color: #94a3b8;
}

.dark .item-card {
  background: #1e293b;
  border-color: #334155;
}

.dark .item-card-header h3 {
  color: #e2e8f0;
}

.dark .item-card p {
  color: #94a3b8;
}

.dark .detail-content {
  color: #cbd5e1;
}

.dark .detail-content :deep(th) {
  background: #334155;
}

.dark .detail-content :deep(code) {
  background: #334155;
  color: #e2e8f0;
}

.dark .search-input .el-input__wrapper {
  background-color: #1e293b;
  box-shadow: 0 0 0 1px #475569 inset;
}
</style>
