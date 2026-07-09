<template>
  <div class="my-kb-page">
    <div class="page-header">
      <h1>我的知识库</h1>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新建知识库
      </el-button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <!-- 知识库列表 -->
    <div v-else class="kb-grid">
      <div
        v-for="kb in knowledgeBases"
        :key="kb.id"
        class="kb-card"
        @click="$router.push(`/kb/${kb.id}`)"
      >
        <div class="kb-card-header">
          <div class="kb-icon">
            <el-icon><Collection /></el-icon>
          </div>
          <div class="kb-tags">
            <el-tag size="small" v-if="kb.is_public" type="success">公开</el-tag>
            <el-tag size="small" v-if="kb.is_official" type="warning">官方</el-tag>
          </div>
        </div>
        <h3>{{ kb.name }}</h3>
        <p>{{ kb.description || '暂无描述' }}</p>
        <div class="kb-footer">
          <span><el-icon><Document /></el-icon> {{ kb.doc_count }} 篇文档</span>
          <span class="kb-time">{{ formatDate(kb.created_at) }}</span>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="knowledgeBases.length === 0" class="empty-state">
        <el-empty description="暂无知识库">
          <el-button type="primary" @click="showCreateDialog = true">
            创建第一个知识库
          </el-button>
        </el-empty>
      </div>
    </div>

    <!-- 创建对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建知识库" width="480px" :close-on-click-modal="false">
      <el-form :model="createForm" :rules="rules" ref="formRef" label-position="top">
        <el-form-item label="名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入知识库名称" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="createForm.description" type="textarea" :rows="3" placeholder="请输入描述（可选）" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item label="可见性">
          <el-switch v-model="createForm.is_public" active-text="公开" inactive-text="私有" />
          <div class="form-tip">公开知识库将显示在知识库广场</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Collection, Document, Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getMyKnowledgeBases, createKnowledgeBase } from '../api/knowledgeBase'

const knowledgeBases = ref([])
const loading = ref(true)
const creating = ref(false)
const showCreateDialog = ref(false)
const formRef = ref(null)
const createForm = ref({ name: '', description: '', is_public: false })

const rules = {
  name: [
    { required: true, message: '请输入知识库名称', trigger: 'blur' },
    { min: 1, max: 50, message: '名称长度为 1-50 个字符', trigger: 'blur' }
  ]
}

onMounted(async () => {
  await loadData()
})

async function loadData() {
  loading.value = true
  try {
    const { data } = await getMyKnowledgeBases()
    knowledgeBases.value = data.items || []
  } catch (e) {
    console.error('加载知识库失败:', e)
    ElMessage.error('加载知识库失败')
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

async function handleCreate() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  creating.value = true
  try {
    await createKnowledgeBase(createForm.value)
    showCreateDialog.value = false
    createForm.value = { name: '', description: '', is_public: false }
    ElMessage.success('创建成功')
    await loadData()
  } catch (e) {
    ElMessage.error('创建失败')
  } finally {
    creating.value = false
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
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
  cursor: pointer;
  border: 1px solid #e4e7ed;
  transition: all 0.2s;
}

.kb-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.kb-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
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
}

.kb-tags {
  display: flex;
  gap: 4px;
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
}

.kb-footer span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.empty-state {
  grid-column: 1 / -1;
}

.form-tip {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}
</style>
