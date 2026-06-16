<template>
  <el-card
    shadow="hover"
    class="plan-card card-hover"
    :class="getCardClass(plan.risk_level)"
  >
    <div class="risk-badge" :class="getBadgeClass(plan.risk_level)">
      {{ plan.risk_level }}
    </div>

    <div class="garment-header">
      <div
        class="color-block"
        :style="{ background: getColorCode(plan.garment.color) }"
      ></div>
      <div class="garment-meta">
        <h3>{{ plan.garment.name }}</h3>
        <div class="tags">
          <el-tag size="small" effect="plain">{{ plan.garment.category }}</el-tag>
          <el-tag size="small" :type="getFabricTagType(plan.garment.fabric)" effect="plain">
            {{ plan.garment.fabric }}
          </el-tag>
          <el-tag size="small" effect="plain">{{ plan.garment.size }}</el-tag>
        </div>
      </div>
    </div>

    <div class="plan-info">
      <div class="info-row">
        <el-icon color="#7e57c2"><Calendar /></el-icon>
        <span class="label">建议洗护：</span>
        <span class="value date-value" :class="{ overdue: plan.overdue_days > 0 }">
          {{ plan.suggested_wash_date }}
        </span>
        <el-tag v-if="plan.overdue_days > 0" type="danger" effect="light" size="small">
          逾期 {{ plan.overdue_days }} 天
        </el-tag>
      </div>
      <div class="info-row">
        <el-icon color="#26a69a"><Brush /></el-icon>
        <span class="label">建议方式：</span>
        <span class="value">{{ plan.suggested_wash_method }}</span>
      </div>
    </div>

    <div class="metrics-grid">
      <div class="metric">
        <div class="metric-label">已穿着次数</div>
        <div class="metric-value">{{ plan.uses_since_last_wash }} 次</div>
      </div>
      <div class="metric">
        <div class="metric-label">距上次洗护</div>
        <div class="metric-value">{{ plan.days_since_last_wash }} 天</div>
      </div>
    </div>

    <div class="trigger-reason">
      <el-icon color="#7e57c2"><InfoFilled /></el-icon>
      <span>{{ plan.trigger_reason }}</span>
    </div>

    <div class="storage-info" v-if="plan.garment.storage_zone">
      <el-icon color="#8d6e63"><Box /></el-icon>
      <span>{{ plan.garment.storage_zone.name }}</span>
    </div>

    <div class="card-actions">
      <el-button type="warning" @click="$emit('record-wash')">
        <el-icon><Brush /></el-icon>
        记录洗护
      </el-button>
      <el-button type="primary" @click="$emit('open-detail')">
        <el-icon><View /></el-icon>
        查看详情
      </el-button>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import type { WashPlan } from '@/types'
import { Calendar, Brush, InfoFilled, Box, View } from '@element-plus/icons-vue'

defineProps<{
  plan: WashPlan
}>()

defineEmits(['open-detail', 'record-wash'])

const getColorCode = (color: string) => {
  const map: Record<string, string> = {
    '粉色': '#f8bbd0', '黑色': '#424242', '白色': '#fafafa',
    '红色': '#ef5350', '蓝色': '#42a5f5', '紫色': '#ab47bc',
    '米色': '#d7ccc8', '肤色': '#ffccbc', '绿色': '#66bb6a',
    '灰色': '#9e9e9e', '棕色': '#8d6e63', '黄色': '#ffee58'
  }
  return map[color] || '#e0e0e0'
}

const getFabricTagType = (fabric: string) => {
  const map: Record<string, string> = {
    '纯棉': 'success', '真丝': 'warning', '蕾丝': 'danger',
    '莫代尔': 'success', '锦纶': 'info', '氨纶': 'warning',
    '聚酯纤维': 'info', '竹纤维': 'success', '羊毛': 'warning'
  }
  return (map[fabric] as any) || ''
}

const getCardClass = (risk: string) => {
  if (risk === '高风险') return 'card-high-risk'
  if (risk === '中风险') return 'card-med-risk'
  if (risk === '低风险') return 'card-low-risk'
  if (risk === '待处理') return 'card-pending'
  return 'card-normal'
}

const getBadgeClass = (risk: string) => {
  if (risk === '高风险') return 'badge-high-risk'
  if (risk === '中风险') return 'badge-med-risk'
  if (risk === '低风险') return 'badge-low-risk'
  if (risk === '待处理') return 'badge-pending'
  return 'badge-normal'
}
</script>

<style scoped>
.plan-card {
  position: relative;
  margin-bottom: 20px;
  border-radius: 16px;
  border: 2px solid transparent;
}

.card-high-risk {
  border-color: #fecaca;
  background: linear-gradient(180deg, #fff 0%, #fef2f2 100%);
}

.card-med-risk {
  border-color: #fde68a;
  background: linear-gradient(180deg, #fff 0%, #fffbeb 100%);
}

.card-low-risk {
  border-color: #bfdbfe;
  background: linear-gradient(180deg, #fff 0%, #eff6ff 100%);
}

.card-pending {
  border-color: #fed7aa;
  background: linear-gradient(180deg, #fff 0%, #fff7ed 100%);
}

.card-normal {
  border-color: #bbf7d0;
  background: linear-gradient(180deg, #fff 0%, #f0fdf4 100%);
}

.risk-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  padding: 6px 14px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
  z-index: 10;
}

.badge-high-risk {
  background: #ef5350;
  color: white;
  animation: pulse 2s infinite;
}

.badge-med-risk {
  background: #ffa726;
  color: white;
}

.badge-low-risk {
  background: #42a5f5;
  color: white;
}

.badge-pending {
  background: #f57c00;
  color: white;
}

.badge-normal {
  background: #66bb6a;
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

.plan-info {
  margin-bottom: 12px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.info-row .label {
  color: #8d6e63;
}

.info-row .value {
  color: #5d4037;
  font-weight: 500;
}

.info-row .date-value.overdue {
  color: #ef4444;
  font-weight: 600;
}

.metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin: 16px 0;
}

.metric .metric-label {
  font-size: 12px;
  color: #8d6e63;
  margin-bottom: 4px;
}

.metric .metric-value {
  font-size: 16px;
  font-weight: 600;
  color: #5d4037;
}

.trigger-reason {
  background: rgba(0, 0, 0, 0.03);
  border-radius: 8px;
  padding: 10px 14px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  color: #5d4037;
  font-size: 13px;
  line-height: 1.5;
  margin-bottom: 12px;
}

.card-high-risk .trigger-reason {
  background: rgba(239, 68, 68, 0.08);
  color: #b91c1c;
}

.card-med-risk .trigger-reason {
  background: rgba(245, 158, 11, 0.08);
  color: #b45309;
}

.storage-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #8d6e63;
  margin-bottom: 16px;
}

.card-actions {
  display: flex;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}
</style>
