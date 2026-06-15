<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon color="#ff5722"><Bell /></el-icon>
        更换提醒
      </h2>
      <div class="header-actions">
        <el-radio-group v-model="urgencyFilter" size="large" @change="filterReminders">
          <el-radio-button value="">全部 ({{ reminders.length }})</el-radio-button>
          <el-radio-button value="立即更换">
            <span style="color: #dc2626">立即更换 ({{ urgentCount }})</span>
          </el-radio-button>
          <el-radio-button value="建议更换">
            <span style="color: #d97706">建议更换 ({{ replaceCount }})</span>
          </el-radio-button>
          <el-radio-button value="注意观察">
            <span style="color: #2563eb">注意观察 ({{ noticeCount }})</span>
          </el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <el-alert
      v-if="urgentCount > 0"
      type="error"
      :closable="false"
      style="margin-bottom: 24px"
      show-icon
    >
      <template #title>
        有 <strong>{{ urgentCount }}</strong> 件衣物需要立即更换，建议尽快处理
      </template>
      这些衣物已超过推荐使用周期或存在严重变形，继续穿着可能影响舒适度和健康。
    </el-alert>

    <el-row :gutter="20">
      <el-col :span="8" v-for="item in filteredReminders" :key="item.garment.id">
        <el-card
          shadow="hover"
          class="reminder-card card-hover"
          :class="getCardClass(item.urgency)"
        >
          <div class="urgency-badge" :class="getBadgeClass(item.urgency)">
            {{ item.urgency }}
          </div>

          <div class="garment-header">
            <div
              class="color-block"
              :style="{ background: getColorCode(item.garment.color) }"
            ></div>
            <div class="garment-meta">
              <h3>{{ item.garment.name }}</h3>
              <div class="tags">
                <el-tag size="small" effect="plain">{{ item.garment.category }}</el-tag>
                <el-tag size="small" type="info" effect="plain">{{ item.garment.fabric }}</el-tag>
                <el-tag size="small" effect="plain">{{ item.garment.size }}</el-tag>
              </div>
            </div>
          </div>

          <div class="reason-box">
            <el-icon><WarningFilled /></el-icon>
            <span>{{ item.reason }}</span>
          </div>

          <el-progress
            v-if="item.garment.replacement_status"
            :percentage="Math.min(100, Math.round(item.garment.replacement_status.overall_score * 100))"
            :color="getProgressColor(item.urgency)"
            :stroke-width="10"
            style="margin: 20px 0"
          />

          <div class="detail-grid">
            <div class="detail-item">
              <div class="label">使用次数</div>
              <div class="value">
                <span :class="{ danger: item.garment.replacement_status?.use_ratio >= 0.9 }">
                  {{ item.garment.use_count }}
                </span>
                <span class="sub">
                  / {{ item.garment.replacement_status?.recommended_uses || '-' }}
                </span>
              </div>
            </div>
            <div class="detail-item">
              <div class="label">使用时长</div>
              <div class="value">
                <span :class="{ danger: item.garment.replacement_status?.time_ratio >= 0.9 }">
                  {{ getMonthsOwned(item.garment.purchase_date) }}
                </span>
                <span class="sub">
                  / {{ item.garment.replacement_status?.replacement_months || '-' }}月
                </span>
              </div>
            </div>
            <div class="detail-item">
              <div class="label">洗护次数</div>
              <div class="value">{{ item.garment.wash_count }} 次</div>
            </div>
            <div class="detail-item">
              <div class="label">变形情况</div>
              <div class="value">
                <span
                  :class="getDeformationClass(item.garment.current_deformation)"
                >
                  {{ item.garment.current_deformation }}
                </span>
              </div>
            </div>
          </div>

          <el-divider v-if="item.garment.replacement_status?.reasons?.length" />

          <div class="reasons-list" v-if="item.garment.replacement_status?.reasons?.length">
            <h4>详细诊断</h4>
            <ul>
              <li v-for="(r, i) in item.garment.replacement_status.reasons" :key="i">
                <el-icon><CaretRight /></el-icon>
                {{ r }}
              </li>
            </ul>
          </div>

          <div class="card-actions">
            <el-button type="primary" @click="handleReplaced(item.garment.id)">
              <el-icon><Check /></el-icon>
              已更换，停用此件
            </el-button>
            <el-button type="info" @click="handleIgnore(item.garment.id)">
              <el-icon><View /></el-icon>
              查看详情
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <div v-if="filteredReminders.length === 0" class="empty-container">
      <el-card shadow="never" class="stats-card empty-card">
        <div class="empty-state">
          <el-icon><CircleCheckFilled /></el-icon>
          <h3>太棒了！</h3>
          <p>{{ urgencyFilter ? '当前筛选条件下没有需要关注的衣物' : '所有衣物状态良好，暂无更换提醒' }}</p>
          <p style="margin-top: 8px; font-size: 13px; color: #a1887f">
            系统将持续监控每一件衣物的使用次数、使用时长和变形情况
          </p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { reminderApi, garmentApi } from '@/api'
import type { ReplacementReminder } from '@/types'
import {
  Bell, WarningFilled, CaretRight, Check, View,
  CircleCheckFilled
} from '@element-plus/icons-vue'

const emit = defineEmits(['refresh-reminders'])

const reminders = ref<ReplacementReminder[]>([])
const urgencyFilter = ref('')

const urgentCount = computed(() => reminders.value.filter(r => r.urgency === '立即更换').length)
const replaceCount = computed(() => reminders.value.filter(r => r.urgency === '建议更换').length)
const noticeCount = computed(() => reminders.value.filter(r => r.urgency === '注意观察').length)

const filteredReminders = computed(() => {
  if (!urgencyFilter.value) return reminders.value
  return reminders.value.filter(r => r.urgency === urgencyFilter.value)
})

const getColorCode = (color: string) => {
  const map: Record<string, string> = {
    '粉色': '#f8bbd0', '黑色': '#424242', '白色': '#fafafa',
    '红色': '#ef5350', '蓝色': '#42a5f5', '紫色': '#ab47bc',
    '米色': '#d7ccc8', '肤色': '#ffccbc', '绿色': '#66bb6a',
    '灰色': '#9e9e9e', '棕色': '#8d6e63', '黄色': '#ffee58'
  }
  return map[color] || '#e0e0e0'
}

const getCardClass = (urgency: string) => {
  if (urgency === '立即更换') return 'card-urgent'
  if (urgency === '建议更换') return 'card-warning'
  return 'card-notice'
}

const getBadgeClass = (urgency: string) => {
  if (urgency === '立即更换') return 'badge-urgent'
  if (urgency === '建议更换') return 'badge-warning'
  return 'badge-notice'
}

const getProgressColor = (urgency: string) => {
  if (urgency === '立即更换') return '#ef5350'
  if (urgency === '建议更换') return '#ffa726'
  return '#42a5f5'
}

const getDeformationClass = (level: string) => {
  if (level === '严重' || level === '中度') return 'danger'
  if (level === '轻微') return 'warning-text'
  return ''
}

const getMonthsOwned = (purchaseDate: string) => {
  const days = Math.floor((Date.now() - new Date(purchaseDate).getTime()) / (1000 * 60 * 60 * 24))
  const months = Math.floor(days / 30.44)
  return months >= 12 ? `${(months / 12).toFixed(1)}年` : `${months}个月`
}

const filterReminders = () => {}

const loadReminders = async () => {
  try {
    reminders.value = await reminderApi.list()
  } catch (e) {
    ElMessage.error('加载提醒失败')
  }
}

const handleReplaced = async (id: number) => {
  try {
    await ElMessageBox.confirm(
      '确认这件衣物已更换并停用？停用后将不会出现在衣物档案中。',
      '确认停用',
      { type: 'warning', confirmButtonText: '确认停用', cancelButtonText: '取消' }
    )
    await garmentApi.delete(id)
    ElMessage.success('已停用此衣物')
    await loadReminders()
    emit('refresh-reminders')
  } catch {
    // cancelled
  }
}

const handleIgnore = (_id: number) => {
  ElMessage.info('请前往衣物档案页面查看完整详情')
}

onMounted(loadReminders)
</script>

<style scoped>
.reminder-card {
  position: relative;
  margin-bottom: 20px;
  border-radius: 16px;
  border: 2px solid transparent;
}

.card-urgent {
  border-color: #fecaca;
  background: linear-gradient(180deg, #fff 0%, #fef2f2 100%);
}

.card-warning {
  border-color: #fde68a;
  background: linear-gradient(180deg, #fff 0%, #fffbeb 100%);
}

.card-notice {
  border-color: #bfdbfe;
  background: linear-gradient(180deg, #fff 0%, #eff6ff 100%);
}

.urgency-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  padding: 6px 14px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
  z-index: 10;
}

.badge-urgent {
  background: #ef5350;
  color: white;
  animation: pulse 2s infinite;
}

.badge-warning {
  background: #ffa726;
  color: white;
}

.badge-notice {
  background: #42a5f5;
  color: white;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.garment-header {
  display: flex;
  gap: 14px;
  margin-bottom: 16px;
}

.color-block {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  border: 2px solid rgba(0, 0, 0, 0.08);
  flex-shrink: 0;
}

.garment-meta h3 {
  margin: 0 0 8px 0;
  font-size: 17px;
  font-weight: 600;
  color: #5d4037;
}

.tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.reason-box {
  background: rgba(0, 0, 0, 0.03);
  border-radius: 8px;
  padding: 10px 14px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  color: #5d4037;
  font-size: 14px;
  line-height: 1.5;
}

.reason-box .el-icon {
  margin-top: 2px;
  flex-shrink: 0;
}

.card-urgent .reason-box {
  background: rgba(239, 68, 68, 0.08);
  color: #b91c1c;
}

.card-warning .reason-box {
  background: rgba(245, 158, 11, 0.08);
  color: #b45309;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.detail-item .label {
  font-size: 12px;
  color: #8d6e63;
  margin-bottom: 4px;
}

.detail-item .value {
  font-size: 16px;
  font-weight: 600;
  color: #5d4037;
}

.detail-item .value .sub {
  font-size: 12px;
  font-weight: normal;
  color: #a1887f;
}

.detail-item .value .danger {
  color: #ef4444;
}

.danger {
  color: #ef4444;
}

.warning-text {
  color: #f59e0b;
}

.reasons-list h4 {
  font-size: 13px;
  color: #8d6e63;
  margin: 0 0 10px 0;
}

.reasons-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.reasons-list li {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 13px;
  color: #5d4037;
  padding: 4px 0;
}

.card-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.empty-container {
  margin-top: 20px;
}

.empty-card {
  min-height: 300px;
}

.empty-state h3 {
  font-size: 22px;
  color: #5d4037;
  margin: 16px 0 8px;
}

.empty-state .el-icon {
  color: #66bb6a;
}
</style>
