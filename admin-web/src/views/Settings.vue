<template>
  <div class="settings-page">
    <h1>系统设置</h1>
    <el-card>
      <el-form label-width="120px">
        <el-divider content-position="left">LLM 设置</el-divider>
        <el-form-item label="LLM 提供者">
          <el-select v-model="settings.llmProvider" style="width: 200px">
            <el-option label="Ollama" value="ollama" />
            <el-option label="OpenAI" value="openai" />
          </el-select>
        </el-form-item>
        <el-form-item label="LLM 模型">
          <el-input v-model="settings.llmModel" style="width: 300px" />
        </el-form-item>
        
        <el-divider content-position="left">嵌入模型设置</el-divider>
        <el-form-item label="嵌入模型">
          <el-input v-model="settings.embeddingModel" style="width: 300px" placeholder="BAAI/bge-small-zh-v1.5" />
        </el-form-item>
        
        <el-divider content-position="left">分块设置</el-divider>
        <el-form-item label="分块大小">
          <el-input-number v-model="settings.chunkSize" :min="100" :max="2000" />
        </el-form-item>
        <el-form-item label="分块重叠">
          <el-input-number v-model="settings.chunkOverlap" :min="0" :max="500" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSave">保存设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAdminSettings, updateAdminSettings } from '../api'

const settings = ref({
  llmProvider: 'ollama',
  llmModel: 'qwen2:7b',
  embeddingModel: 'BAAI/bge-small-zh-v1.5',
  chunkSize: 500,
  chunkOverlap: 50,
})

onMounted(async () => {
  try {
    const { data } = await getAdminSettings()
    settings.value = {
      llmProvider: data.llm?.provider || 'ollama',
      llmModel: data.llm?.ollama_model || data.llm?.openai_model || 'qwen2:7b',
      embeddingModel: data.embedding?.model || 'BAAI/bge-small-zh-v1.5',
      chunkSize: data.chunking?.chunk_size || 500,
      chunkOverlap: data.chunking?.chunk_overlap || 50,
    }
  } catch (e) {
    console.error('加载设置失败', e)
  }
})

async function handleSave() {
  try {
    await updateAdminSettings({
      llm: {
        provider: settings.value.llmProvider,
        ollama_model: settings.value.llmProvider === 'ollama' ? settings.value.llmModel : undefined,
        openai_model: settings.value.llmProvider === 'openai' ? settings.value.llmModel : undefined,
      },
      embedding: {
        model: settings.value.embeddingModel,
      },
      chunking: {
        chunk_size: settings.value.chunkSize,
        chunk_overlap: settings.value.chunkOverlap,
      },
    })
    ElMessage.success('设置已保存')
  } catch (e) {
    ElMessage.error('保存失败')
  }
}
</script>

<style scoped>
.settings-page h1 {
  margin: 0 0 24px;
  font-size: 24px;
}

.settings-page .el-card {
  max-width: 600px;
}
</style>
