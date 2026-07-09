<template>
  <div class="chat-page">
    <!-- 左侧边栏：对话历史 -->
    <aside class="chat-sidebar">
      <div class="sidebar-header">
        <el-button type="primary" @click="startNewChat">
          <el-icon><Plus /></el-icon>
          新对话
        </el-button>
      </div>
      <div class="sidebar-search">
        <el-input v-model="searchText" placeholder="搜索对话..." size="small" clearable prefix-icon="Search" />
      </div>
      <div class="conversation-list">
        <div
          v-for="conv in filteredConversations"
          :key="conv.id"
          class="conv-item"
          :class="{ active: currentConvId === conv.id }"
          @click="selectConv(conv)"
        >
          <div class="conv-icon">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="conv-info">
            <div class="conv-title">{{ conv.title }}</div>
            <div class="conv-time">{{ formatTime(conv.updated_at) }}</div>
          </div>
          <el-button text circle size="small" class="conv-delete" @click.stop="deleteConv(conv)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
        <el-empty v-if="conversations.length === 0" description="暂无对话" :image-size="60" />
      </div>
    </aside>

    <!-- 主聊天区 -->
    <div class="chat-main">
      <!-- 聊天头部 -->
      <div class="chat-header">
        <div class="header-left">
          <el-select v-model="selectedKB" placeholder="选择知识库" size="small" style="width: 180px">
            <el-option v-for="kb in knowledgeBases" :key="kb.id" :label="kb.name" :value="kb.id" />
          </el-select>
        </div>
        <div class="header-right" v-if="currentConvId">
          <el-dropdown @command="handleExport">
            <el-button text size="small">
              <el-icon><Download /></el-icon> 导出
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="markdown">Markdown 格式</el-dropdown-item>
                <el-dropdown-item command="txt">纯文本格式</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 消息区域 -->
      <div class="chat-messages" ref="messagesRef">
        <!-- 欢迎界面 -->
        <div v-if="messages.length === 0 && !streaming" class="welcome">
          <div class="welcome-icon">💬</div>
          <h2>开始智能问答</h2>
          <p>选择知识库，输入问题，AI 为您精准解答</p>
          <div class="quick-questions">
            <div class="quick-item" v-for="q in quickQuestions" :key="q" @click="askQuick(q)">{{ q }}</div>
          </div>
        </div>

        <!-- 消息列表 -->
        <div v-for="msg in messages" :key="msg.id" class="message" :class="msg.role">
          <div class="message-avatar">
            <span v-if="msg.role === 'user'">我</span>
            <el-icon v-else><Monitor /></el-icon>
          </div>
          <div class="message-content">
            <div class="message-text" v-html="formatMessage(msg.content)"></div>
            <div class="message-actions" v-if="msg.role === 'assistant'">
              <el-button text size="small" @click="copyMessage(msg.content)">
                <el-icon><CopyDocument /></el-icon> 复制
              </el-button>
              <el-button
                text
                size="small"
                :class="{ 'feedback-active': msg.userFeedback === 'like' }"
                @click="handleFeedback(msg, 'like')"
              >
                <el-icon><Top /></el-icon> 有用
              </el-button>
              <el-button
                text
                size="small"
                :class="{ 'feedback-active': msg.userFeedback === 'dislike' }"
                @click="handleFeedback(msg, 'dislike')"
              >
                <el-icon><Bottom /></el-icon> 无用
              </el-button>
            </div>
            <!-- 来源引用 -->
            <div v-if="msg.sources && msg.sources.length > 0" class="message-sources">
              <div class="sources-title">
                <el-icon><Link /></el-icon> 参考来源
              </div>
              <div v-for="(source, idx) in msg.sources" :key="idx" class="source-item">
                <span class="source-index">{{ idx + 1 }}</span>
                <span class="source-content">{{ source.content?.substring(0, 100) }}...</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 流式输出 -->
        <div v-if="streaming" class="message assistant">
          <div class="message-avatar"><el-icon><Monitor /></el-icon></div>
          <div class="message-content">
            <div class="message-text" v-html="formatMessage(streamingText)"></div>
            <span class="typing-cursor">|</span>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input-area">
        <div class="input-container">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="1"
            :autosize="{ minRows: 1, maxRows: 4 }"
            placeholder="输入您的问题... (Enter 发送，Shift+Enter 换行)"
            @keydown="handleKeydown"
            :disabled="!selectedKB"
            resize="none"
          />
          <el-button type="primary" circle size="large" :disabled="!inputMessage.trim() || !selectedKB" :loading="streaming" @click="sendMessage">
            <el-icon v-if="!streaming"><Promotion /></el-icon>
          </el-button>
        </div>
        <div class="input-hint">
          <span v-if="!selectedKB">请先选择知识库</span>
          <span v-else>Enter 发送 · Shift+Enter 换行</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, ChatDotRound, Delete, Promotion, Search, Monitor, CopyDocument, Link, Top, Bottom, Download } from '@element-plus/icons-vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import {
  getConversations, createConversation, getMessages, deleteConversation,
  getMyKnowledgeBases, chatStream, submitFeedback
} from '../api/knowledgeBase'

const route = useRoute()
const conversations = ref([])
const knowledgeBases = ref([])
const currentConvId = ref(null)
const messages = ref([])
const inputMessage = ref('')
const selectedKB = ref('')
const streaming = ref(false)
const streamingText = ref('')
const streamingSources = ref([])
const messagesRef = ref(null)
const searchText = ref('')

const quickQuestions = ['这个知识库包含哪些内容？', '帮我总结一下主要观点', '有哪些重要的概念？']

const filteredConversations = computed(() => {
  if (!searchText.value) return conversations.value
  return conversations.value.filter(c => c.title.toLowerCase().includes(searchText.value.toLowerCase()))
})

onMounted(async () => {
  try {
    const [convRes, kbRes] = await Promise.all([getConversations(), getMyKnowledgeBases()])
    conversations.value = convRes.data
    knowledgeBases.value = kbRes.data.items || []
    
    // 优先使用 kbId 查询参数选中知识库
    const kbId = route.query.kbId
    if (kbId && knowledgeBases.value.some(kb => kb.id === kbId)) {
      selectedKB.value = kbId
    } else if (knowledgeBases.value.length > 0) {
      selectedKB.value = knowledgeBases.value[0].id
    }
    
    // 如果有 convId query 参数，自动打开该对话
    const convId = route.query.convId
    if (convId) {
      const conv = conversations.value.find(c => c.id === convId)
      if (conv) {
        selectConv(conv)
      }
    }
  } catch (e) {
    console.error('加载数据失败:', e)
    ElMessage.error('加载数据失败，请刷新页面重试')
  }
})

function formatMessage(content) {
  return content ? DOMPurify.sanitize(marked.parse(content, { breaks: true })) : ''
}

function formatTime(dateStr) {
  const days = Math.floor((new Date() - new Date(dateStr)) / 86400000)
  if (days < 1) return '今天'
  if (days < 7) return days + '天前'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() }
}

function askQuick(q) { inputMessage.value = q; sendMessage() }

async function startNewChat() {
  if (!selectedKB.value) { ElMessage.warning('请先选择知识库'); return }
  try {
    const { data } = await createConversation({ knowledge_base_id: selectedKB.value, title: '新对话' })
    conversations.value.unshift(data)
    selectConv(data)
  } catch (e) {
    console.error('创建对话失败:', e)
    ElMessage.error('创建对话失败')
  }
}

async function selectConv(conv) {
  currentConvId.value = conv.id
  try {
    const { data } = await getMessages(conv.id)
    messages.value = (data || []).map(msg => ({ ...msg, isTemp: false }))
    scrollToBottom()
  } catch (e) {
    console.error('加载消息失败:', e)
    ElMessage.error('加载消息失败')
  }
}

async function deleteConv(conv) {
  try {
    await ElMessageBox.confirm('确定删除该对话？', '确认')
    await deleteConversation(conv.id)
    conversations.value = conversations.value.filter(c => c.id !== conv.id)
    if (currentConvId.value === conv.id) {
      currentConvId.value = null
      messages.value = []
    }
    ElMessage.success('删除成功')
  } catch (e) {
    if (e !== 'cancel') {
      console.error('删除失败:', e)
      ElMessage.error('删除失败')
    }
  }
}

async function sendMessage() {
  if (!inputMessage.value.trim() || streaming.value) return
  if (!selectedKB.value) { ElMessage.warning('请先选择知识库'); return }
  const msg = inputMessage.value
  inputMessage.value = ''

  // 添加临时用户消息（标记为临时）
  const tempUserMsg = { id: `temp_${Date.now()}`, role: 'user', content: msg, isTemp: true }
  messages.value.push(tempUserMsg)
  scrollToBottom()

  if (!currentConvId.value) {
    try {
      const { data } = await createConversation({ knowledge_base_id: selectedKB.value, title: msg.slice(0, 50) })
      conversations.value.unshift(data)
      currentConvId.value = data.id
    } catch (e) {
      console.error('创建对话失败:', e)
      ElMessage.error('创建对话失败，请重试')
      inputMessage.value = msg
      streaming.value = false
      return
    }
  }

  streaming.value = true; streamingText.value = ''; streamingSources.value = []
  try {
    await chatStream({ conversation_id: currentConvId.value, knowledge_base_id: selectedKB.value, message: msg },
      (chunk) => { streamingText.value += chunk; scrollToBottom() },
      (sources) => { streamingSources.value = sources || [] },
      () => {
        // 添加临时助手消息
        const tempAssistantMsg = {
          id: `temp_${Date.now()}`,
          role: 'assistant',
          content: streamingText.value,
          sources: streamingSources.value,
          isTemp: true
        }
        messages.value.push(tempAssistantMsg)
        streaming.value = false
        streamingText.value = ''
        streamingSources.value = []

        // 异步从服务器加载真实消息，替换临时消息
        refreshMessages()
      }
    )
  } catch (e) {
    console.error('聊天失败:', e)
    ElMessage.error('发送消息失败，请重试')
    streaming.value = false
    streamingText.value = ''
    streamingSources.value = []
  }
}

async function refreshMessages() {
  if (!currentConvId.value) return
  try {
    const { data } = await getMessages(currentConvId.value)
    if (data && data.length > 0) {
      // 用服务器数据替换所有临时消息
      messages.value = data.map(msg => ({ ...msg, isTemp: false }))
    }
  } catch (e) {
    // 静默失败，保留临时消息
  }
}

async function copyMessage(content) {
  try {
    await navigator.clipboard.writeText(content)
    ElMessage.success('已复制到剪贴板')
  } catch (e) {
    ElMessage.error('复制失败')
  }
}

async function handleExport(format) {
  if (!currentConvId.value) {
    ElMessage.warning('请先选择对话')
    return
  }

  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`/api/conversations/${currentConvId.value}/export?format=${format}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('导出失败')
    }

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url

    // 获取文件名（清理非法字符）
    const conv = conversations.value.find(c => c.id === currentConvId.value)
    let filename = conv ? conv.title : '对话导出'
    filename = filename.replace(/[\/\\:*?"<>|]/g, '_').trim() || '对话导出'

    a.download = `${filename}.${format === 'markdown' ? 'md' : 'txt'}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)

    ElMessage.success('导出成功')
  } catch (e) {
    console.error('导出失败:', e)
    ElMessage.error('导出失败')
  }
}

async function handleFeedback(msg, type) {
  // 防止重复提交
  if (msg.userFeedback === type) return

  // 如果消息是临时消息（未保存到服务器），先刷新消息列表
  if (msg.isTemp || (msg.id && msg.id.startsWith('temp_'))) {
    await refreshMessages()
    // 刷新后找到对应的消息
    const realMsg = messages.value.find(m => m.content === msg.content && m.role === msg.role)
    if (!realMsg || realMsg.isTemp || (realMsg.id && realMsg.id.startsWith('temp_'))) {
      ElMessage.warning('消息尚未保存，请稍后再试')
      return
    }
    msg = realMsg
  }

  try {
    await submitFeedback({
      message_id: msg.id,
      conversation_id: currentConvId.value,
      rating: type === 'like' ? 5 : 1,
      comment: type === 'like' ? '有用' : '无用'
    })
    msg.userFeedback = type
    ElMessage.success(type === 'like' ? '感谢您的反馈' : '已记录，我们会继续改进')
  } catch (e) {
    ElMessage.error('反馈提交失败')
  }
}

function scrollToBottom() {
  nextTick(() => { if (messagesRef.value) messagesRef.value.scrollTop = messagesRef.value.scrollHeight })
}
</script>

<style scoped>
.chat-page {
  display: flex;
  height: calc(100vh - 64px - 48px);
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.chat-sidebar {
  width: 260px;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.sidebar-search {
  padding: 12px 16px;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px;
}

.conv-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 4px;
  transition: background 0.2s;
}

.conv-item:hover { background: #e2e8f0; }
.conv-item.active { background: #dbeafe; }

.conv-icon {
  width: 32px;
  height: 32px;
  background: #e2e8f0;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  flex-shrink: 0;
}

.conv-item.active .conv-icon { background: #3b82f6; color: #fff; }

.conv-info { flex: 1; min-width: 0; }

.conv-title { font-size: 14px; font-weight: 500; color: #1e293b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.conv-time { font-size: 12px; color: #94a3b8; margin-top: 2px; }
.conv-delete { opacity: 0; transition: opacity 0.2s; }
.conv-item:hover .conv-delete { opacity: 1; }

.chat-main { flex: 1; display: flex; flex-direction: column; }

.chat-header {
  padding: 12px 20px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left, .header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chat-messages { flex: 1; overflow-y: auto; padding: 24px; }

.welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
}

.welcome-icon { font-size: 56px; margin-bottom: 16px; }
.welcome h2 { margin: 0 0 8px; font-size: 24px; color: #1e293b; }
.welcome > p { margin: 0 0 24px; color: #64748b; }

.quick-questions { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; }

.quick-item {
  padding: 8px 16px;
  background: #f1f5f9;
  border-radius: 20px;
  font-size: 13px;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-item:hover { background: #e2e8f0; color: #1e293b; }

.message { display: flex; gap: 12px; margin-bottom: 16px; max-width: 750px; }
.message.user { flex-direction: row-reverse; margin-left: auto; }

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}

.message.user .message-avatar { background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: #fff; }
.message.assistant .message-avatar { background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color: #fff; }

.message-text {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.7;
}

.message.user .message-text { background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: #fff; border-bottom-right-radius: 4px; }
.message.assistant .message-text { background: #f1f5f9; color: #1e293b; border-bottom-left-radius: 4px; }

.message-text :deep(p) { margin: 0 0 8px; }
.message-text :deep(p:last-child) { margin-bottom: 0; }
.message-text :deep(code) { background: rgba(0,0,0,0.06); padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 13px; }

.message-actions {
  margin-top: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.message:hover .message-actions {
  opacity: 1;
}

.message-actions .el-button {
  font-size: 12px;
  color: #94a3b8;
}

.message-actions .el-button:hover {
  color: #3b82f6;
}

.message-actions .el-button.feedback-active {
  color: #3b82f6;
  font-weight: 500;
}

/* 来源引用样式 */
.message-sources {
  margin-top: 12px;
  padding: 12px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.sources-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: #64748b;
  margin-bottom: 8px;
}

.source-item {
  display: flex;
  gap: 8px;
  padding: 8px;
  background: #f8fafc;
  border-radius: 6px;
  margin-bottom: 6px;
  font-size: 12px;
}

.source-item:last-child {
  margin-bottom: 0;
}

.source-index {
  width: 20px;
  height: 20px;
  background: #3b82f6;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  flex-shrink: 0;
}

.source-content {
  color: #475569;
  line-height: 1.5;
}

.typing-cursor { animation: blink 1s infinite; color: #3b82f6; }
@keyframes blink { 0%, 50% { opacity: 1; } 51%, 100% { opacity: 0; } }

.chat-input-area {
  padding: 16px 20px;
  border-top: 1px solid #e2e8f0;
  background: #fff;
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  background: #f1f5f9;
  border-radius: 12px;
  padding: 12px 16px;
}

.input-container .el-textarea { flex: 1; }
.input-container :deep(.el-textarea__inner) { background: transparent; border: none; box-shadow: none; padding: 0; }
.input-hint { margin-top: 8px; font-size: 12px; color: #94a3b8; text-align: center; }
</style>
