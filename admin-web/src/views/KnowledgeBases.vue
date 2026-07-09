<template>
  <div class="kb-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>知识库管理</span>
          <span class="total-count">共 {{ knowledgeBases.length }} 个知识库</span>
        </div>
      </template>

      <!-- 搜索 -->
      <div class="filter-bar">
        <el-input
          v-model="searchText"
          placeholder="搜索知识库..."
          prefix-icon="Search"
          clearable
          style="width: 250px"
        />
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <el-icon class="is-loading" :size="40"><Loading /></el-icon>
        <span>加载中...</span>
      </div>

      <el-table v-else :data="filteredKBs" stripe>
        <el-table-column prop="name" label="名称">
          <template #default="{ row }">
            <div class="kb-name">
              <div class="kb-icon" :class="{ official: row.is_official }">
                <el-icon><Collection /></el-icon>
              </div>
              <div>
                <div class="name-text">{{ row.name }}</div>
                <div class="name-desc">{{ row.description || '暂无描述' }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="doc_count" label="文档数" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.doc_count }} 篇</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="copy_count" label="复制次数" width="100" align="center" />
        <el-table-column prop="is_public" label="可见性" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_public ? 'success' : 'info'" size="small">
              {{ row.is_public ? '公开' : '私有' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_official" label="官方" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_official" type="warning" size="small">官方</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-button text type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && filteredKBs.length === 0" description="暂无知识库" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Collection, Loading } from '@element-plus/icons-vue'
import { getAdminKnowledgeBases, deleteAdminKnowledgeBase } from '../api'

const knowledgeBases = ref([])
const loading = ref(true)
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
  await loadData()
})

async function loadData() {
  loading.value = true
  try {
    const { data } = await getAdminKnowledgeBases()
    knowledgeBases.value = data?.items || data || []
  } catch (e) {
    console.error('加载知识库失败:', e)
    ElMessage.error('加载知识库列表失败')
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

async function handleDelete(kb) {
  try {
    await ElMessageBox.confirm(
      `确定删除知识库「${kb.name}」？此操作将删除所有相关文档和向量数据，且不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await deleteAdminKnowledgeBase(kb.id)
    knowledgeBases.value = knowledgeBases.value.filter(k => k.id !== kb.id)
    ElMessage.success('删除成功')
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.total-count {
  font-size: 14px;
  font-weight: normal;
  color: #909399;
}

.filter-bar {
  margin-bottom: 16px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 60px 0;
  color: #94a3b8;
}

.kb-name {
  display: flex;
  align-items: center;
  gap: 12px;
}

.kb-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  flex-shrink: 0;
}

.kb-icon.official {
  background: linear-gradient(135deg, #22c55e, #16a34a);
}

.name-text {
  font-weight: 500;
  color: #1e293b;
}

.name-desc {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 2px;
}
</style>
