<template>
  <div class="statistics-page">
    <h1>数据统计</h1>

    <!-- 总览数据 -->
    <div class="overview-grid">
      <div class="overview-card">
        <div class="overview-icon blue">
          <el-icon :size="24"><User /></el-icon>
        </div>
        <div class="overview-info">
          <div class="overview-value">{{ overview.userCount }}</div>
          <div class="overview-label">总用户数</div>
        </div>
      </div>
      <div class="overview-card">
        <div class="overview-icon green">
          <el-icon :size="24"><Document /></el-icon>
        </div>
        <div class="overview-info">
          <div class="overview-value">{{ overview.fileCount }}</div>
          <div class="overview-label">总文件数</div>
        </div>
      </div>
      <div class="overview-card">
        <div class="overview-icon orange">
          <el-icon :size="24"><ChatDotRound /></el-icon>
        </div>
        <div class="overview-info">
          <div class="overview-value">{{ overview.msgCount }}</div>
          <div class="overview-label">总消息数</div>
        </div>
      </div>
    </div>

    <!-- 详细统计 -->
    <div class="stats-grid">
      <!-- 用户增长 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>用户增长趋势</span>
          </div>
        </template>
        <div v-if="userStats.length > 0" class="chart-content">
          <div class="bar-chart">
            <div v-for="item in userStats" :key="item.date" class="bar-item">
              <div class="bar-label">{{ formatDate(item.date) }}</div>
              <div class="bar-container">
                <div class="bar-fill blue" :style="{ width: getBarWidth(item.count, maxUserCount) }"></div>
              </div>
              <div class="bar-value">{{ item.count }}</div>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无数据" :image-size="80" />
      </el-card>

      <!-- 对话统计 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>对话量趋势</span>
          </div>
        </template>
        <div v-if="trendStats.length > 0" class="chart-content">
          <div class="bar-chart">
            <div v-for="item in trendStats" :key="item.date" class="bar-item">
              <div class="bar-label">{{ formatDate(item.date) }}</div>
              <div class="bar-container">
                <div class="bar-fill green" :style="{ width: getBarWidth(item.count, maxTrendCount) }"></div>
              </div>
              <div class="bar-value">{{ item.count }}</div>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无数据" :image-size="80" />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { User, Collection, Document, ChatDotRound } from '@element-plus/icons-vue'
import { getOverviewStats, getUserStats, getTrends } from '../api'

const overview = ref({
  userCount: 0,
  kbCount: 0,
  docCount: 0,
  msgCount: 0
})

const userStats = ref([])
const trendStats = ref([])

const maxUserCount = computed(() => {
  return Math.max(...userStats.value.map(s => s.count), 1)
})

const maxTrendCount = computed(() => {
  return Math.max(...trendStats.value.map(s => s.count), 1)
})

onMounted(async () => {
  try {
    const [overviewRes, userRes, trendRes] = await Promise.all([
      getOverviewStats(),
      getUserStats().catch(() => ({ data: [] })),
      getTrends().catch(() => ({ data: [] }))
    ])

    overview.value = {
      userCount: overviewRes.data.user_count || 0,
      fileCount: overviewRes.data.file_count || 0,
      msgCount: overviewRes.data.message_count || 0
    }

    userStats.value = userRes.data || []
    trendStats.value = trendRes.data || []
  } catch (e) {
    console.error('加载统计数据失败:', e)
  }
})

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

function getBarWidth(count, max) {
  return `${(count / max) * 100}%`
}
</script>

<style scoped>
.statistics-page h1 {
  margin: 0 0 24px;
  font-size: 24px;
}

/* 总览卡片 */
.overview-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.overview-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.overview-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.overview-icon.blue { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.overview-icon.green { background: linear-gradient(135deg, #22c55e, #16a34a); }
.overview-icon.purple { background: linear-gradient(135deg, #a855f7, #9333ea); }
.overview-icon.orange { background: linear-gradient(135deg, #f97316, #ea580c); }

.overview-info {
  flex: 1;
}

.overview-value {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

.overview-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 2px;
}

/* 图表卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.chart-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.chart-content {
  padding: 8px 0;
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bar-label {
  width: 60px;
  font-size: 12px;
  color: #64748b;
  text-align: right;
}

.bar-container {
  flex: 1;
  height: 24px;
  background: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.bar-fill.blue {
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
}

.bar-fill.green {
  background: linear-gradient(90deg, #22c55e, #4ade80);
}

.bar-value {
  width: 40px;
  font-size: 13px;
  font-weight: 500;
  color: #1e293b;
}
</style>
