<template>
  <div class="not-found">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <h2>页面不存在</h2>
      <p>抱歉，您访问的页面不存在或已被移除</p>
      <el-button type="primary" @click="$router.push('/dashboard')">返回仪表盘</el-button>
    </div>
  </div>
</template>

<style scoped>
.not-found {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

.not-found-content {
  text-align: center;
}

.error-code {
  font-size: 120px;
  font-weight: 700;
  color: #e2e8f0;
  line-height: 1;
  margin-bottom: 16px;
}

h2 {
  margin: 0 0 12px;
  font-size: 24px;
  color: #1e293b;
}

p {
  margin: 0 0 24px;
  color: #64748b;
}
</style>
