<template>
  <el-container class="layout-container">
    <el-aside width="240px" class="sidebar">
      <div class="logo">
        <el-icon :size="32" color="#ec407a"><Female /></el-icon>
        <h1>内衣管家</h1>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        router
        background-color="transparent"
        text-color="#6d4c41"
        active-text-color="#ec407a"
      >
        <el-menu-item index="/garments">
          <el-icon><Female /></el-icon>
          <span>衣物档案</span>
        </el-menu-item>
        <el-menu-item index="/storage">
          <el-icon><Box /></el-icon>
          <span>收纳分区</span>
        </el-menu-item>
        <el-menu-item index="/wash-records">
          <el-icon><Brush /></el-icon>
          <span>洗护记录</span>
        </el-menu-item>
        <el-menu-item index="/reminders">
          <el-icon><Bell /></el-icon>
          <span>更换提醒</span>
          <el-badge
            v-if="reminderCount > 0"
            :value="reminderCount"
            :max="99"
            class="reminder-badge"
          />
        </el-menu-item>
        <el-menu-item index="/statistics">
          <el-icon><DataLine /></el-icon>
          <span>数据统计</span>
        </el-menu-item>
      </el-menu>
      <div class="sidebar-footer">
        <p>内衣收纳与洗护管理</p>
        <p class="version">v1.0.0</p>
      </div>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon :size="20" color="#8d6e63"><Location /></el-icon>
          <span class="breadcrumb">{{ currentTitle }}</span>
        </div>
        <div class="header-right">
          <el-tag type="warning" effect="light" v-if="reminderCount > 0">
            <el-icon><Bell /></el-icon>
            {{ reminderCount }} 件需关注
          </el-tag>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view @refresh-reminders="loadReminderCount" />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { reminderApi } from '@/api'

const route = useRoute()
const reminderCount = ref(0)

const activeMenu = computed(() => route.path)
const currentTitle = computed(() => (route.meta.title as string) || '首页')

const loadReminderCount = async () => {
  try {
    const reminders = await reminderApi.list()
    reminderCount.value = reminders.length
  } catch (e) {
    console.error(e)
  }
}

onMounted(loadReminderCount)
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background: linear-gradient(180deg, #fff 0%, #fce4ec 100%);
  border-right: 1px solid #f8bbd0;
  display: flex;
  flex-direction: column;
}

.logo {
  padding: 24px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid #f8bbd0;
}

.logo h1 {
  font-size: 20px;
  color: #5d4037;
  font-weight: 600;
  margin: 0;
}

.sidebar-menu {
  flex: 1;
  border: none !important;
  padding-top: 16px;
}

.sidebar-menu .el-menu-item {
  margin: 4px 12px;
  border-radius: 8px;
  height: 48px;
  line-height: 48px;
}

.sidebar-menu .el-menu-item:hover {
  background: #fce4ec;
}

.sidebar-menu .el-menu-item.is-active {
  background: #f8bbd0 !important;
  color: #ad1457 !important;
}

.reminder-badge {
  margin-left: 8px;
}

.sidebar-footer {
  padding: 20px;
  text-align: center;
  border-top: 1px solid #f8bbd0;
  color: #a1887f;
  font-size: 12px;
}

.sidebar-footer .version {
  margin-top: 4px;
  opacity: 0.7;
}

.header {
  background: white;
  border-bottom: 1px solid #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  height: 64px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.breadcrumb {
  font-size: 16px;
  font-weight: 500;
  color: #5d4037;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.main-content {
  background: transparent;
  padding: 0;
  overflow: auto;
}
</style>
