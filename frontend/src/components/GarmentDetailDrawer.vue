<template>
  <el-drawer
    v-model="drawerVisible"
    :title="detail?.name || '衣物详情'"
    direction="rtl"
    size="560px"
    destroy-on-close
    @close="handleClose"
  >
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <p style="margin-top: 12px; color: #8d6e63;">加载中...</p>
    </div>

    <div v-else-if="detail" class="detail-content">
      <div class="garment-header">
        <div
          class="color-block"
          :style="{ background: getColorCode(detail.color) }"
        ></div>
        <div class="header-info">
          <h3>{{ detail.name }}</h3>
          <div class="tags">
            <el-tag size="small" effect="plain">{{ detail.category }}</el-tag>
            <el-tag size="small" :type="getFabricTagType(detail.fabric)" effect="plain">
              {{ detail.fabric }}
            </el-tag>
            <el-tag size="small" effect="plain">{{ detail.size }}</el-tag>
            <el-tag
              v-if="detail.replacement_status"
              :class="getStatusClass(detail.replacement_status.urgency)"
              size="small"
            >
              {{ detail.replacement_status.urgency }}
            </el-tag>
            <el-tag
              v-if="detail.trip_occupancy && detail.trip_occupancy.length > 0"
              type="warning"
              size="small"
              effect="dark"
            >
              <el-icon><Suitcase /></el-icon>
              近期出行占用 ({{ detail.trip_occupancy.length }})
            </el-tag>
          </div>
        </div>
      </div>

      <el-tabs v-model="activeTab" class="detail-tabs">
        <el-tab-pane label="衣物档案" name="basic">
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="品牌">
              {{ detail.brand || '未记录' }}
            </el-descriptions-item>
            <el-descriptions-item label="价格">
              {{ detail.price > 0 ? `¥${detail.price}` : '未记录' }}
            </el-descriptions-item>
            <el-descriptions-item label="购买日期">
              {{ detail.purchase_date }}
            </el-descriptions-item>
            <el-descriptions-item label="使用次数">
              <strong>{{ detail.use_count }}</strong> 次
              <span v-if="detail.replacement_status" class="sub-text">
                / {{ detail.replacement_status.recommended_uses }} 次（推荐）
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="洗护次数">
              <strong>{{ detail.wash_count }}</strong> 次
            </el-descriptions-item>
            <el-descriptions-item label="当前变形">
              <span :class="getDeformationClass(detail.current_deformation)">
                {{ detail.current_deformation }}
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="上次穿着">
              {{ detail.last_worn_date || '从未穿着' }}
            </el-descriptions-item>
            <el-descriptions-item label="上次洗护">
              {{ detail.last_wash_date || '从未洗护' }}
            </el-descriptions-item>
            <el-descriptions-item label="收纳位置">
              <el-icon><Box /></el-icon>
              {{ detail.storage_zone?.name || '未分区' }}
            </el-descriptions-item>
            <el-descriptions-item label="备注" v-if="detail.notes">
              {{ detail.notes }}
            </el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>

        <el-tab-pane label="洗护建议" name="care">
          <div v-if="detail.care_advice" class="care-advice">
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="洗涤方式">
                <el-icon><Brush /></el-icon>
                {{ detail.care_advice.wash_method }}
              </el-descriptions-item>
              <el-descriptions-item label="水温要求">
                <el-icon><Sunny /></el-icon>
                {{ detail.care_advice.wash_temp }}
              </el-descriptions-item>
              <el-descriptions-item label="晾晒方式">
                <el-icon><Sunny /></el-icon>
                {{ detail.care_advice.drying }}
              </el-descriptions-item>
              <el-descriptions-item label="洗涤剂">
                <el-icon><Document /></el-icon>
                {{ detail.care_advice.detergent }}
              </el-descriptions-item>
              <el-descriptions-item label="熨烫">
                <el-icon><Lightning /></el-icon>
                {{ detail.care_advice.iron }}
              </el-descriptions-item>
              <el-descriptions-item label="推荐使用次数">
                <el-icon><Timer /></el-icon>
                {{ detail.care_advice.recommended_uses }} 次
              </el-descriptions-item>
              <el-descriptions-item label="建议更换周期">
                <el-icon><Calendar /></el-icon>
                {{ detail.care_advice.replacement_months }} 个月
              </el-descriptions-item>
              <el-descriptions-item label="注意事项">
                <el-icon><Warning /></el-icon>
                {{ detail.care_advice.notes }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-tab-pane>

        <el-tab-pane label="洗护计划" name="plan">
          <div v-if="detail.next_wash_plan" class="wash-plan-card">
            <div class="plan-header">
              <el-tag
                :class="getRiskClass(detail.next_wash_plan.risk_level)"
                size="large"
              >
                {{ detail.next_wash_plan.risk_level }}
              </el-tag>
              <span class="plan-date">
                <el-icon><Calendar /></el-icon>
                建议洗护：{{ detail.next_wash_plan.suggested_wash_date }}
              </span>
            </div>

            <div class="plan-metrics">
              <div class="metric">
                <div class="label">建议方式</div>
                <div class="value">{{ detail.next_wash_plan.suggested_wash_method }}</div>
              </div>
              <div class="metric">
                <div class="label">逾期天数</div>
                <div class="value" :class="{ danger: detail.next_wash_plan.overdue_days > 0 }">
                  {{ detail.next_wash_plan.overdue_days > 0 ? `${detail.next_wash_plan.overdue_days} 天` : '0 天' }}
                </div>
              </div>
              <div class="metric">
                <div class="label">距上次穿着次数</div>
                <div class="value">{{ detail.next_wash_plan.uses_since_last_wash }} 次</div>
              </div>
              <div class="metric">
                <div class="label">距上次洗护天数</div>
                <div class="value">{{ detail.next_wash_plan.days_since_last_wash }} 天</div>
              </div>
            </div>

            <div class="trigger-reason">
              <el-icon><InfoFilled /></el-icon>
              <span>{{ detail.next_wash_plan.trigger_reason }}</span>
            </div>
          </div>
          <el-empty v-else description="暂无洗护计划" />
        </el-tab-pane>

        <el-tab-pane label="穿着记录" name="wear">
          <el-timeline v-if="detail.recent_wear_records.length">
            <el-timeline-item
              v-for="(r, i) in detail.recent_wear_records"
              :key="r.id"
              :timestamp="r.wear_date"
              :color="r.deformation_noticed !== '无' ? '#f56c6c' : '#67c23a'"
            >
              <h4>{{ r.wear_date }}</h4>
              <p>穿着时长：{{ r.duration_hours }} 小时</p>
              <p v-if="r.deformation_noticed !== '无'">
                变形观察：
                <el-tag :class="getDeformationClass(r.deformation_noticed)" size="small">
                  {{ r.deformation_noticed }}
                </el-tag>
              </p>
              <p v-if="r.notes">备注：{{ r.notes }}</p>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无穿着记录" />
        </el-tab-pane>

        <el-tab-pane label="洗护记录" name="wash">
          <el-timeline v-if="detail.recent_wash_records.length">
            <el-timeline-item
              v-for="(r, i) in detail.recent_wash_records"
              :key="r.id"
              :timestamp="r.wash_date"
              :color="r.deformation_after !== '无' ? '#f56c6c' : '#67c23a'"
            >
              <h4>{{ r.wash_date }}</h4>
              <p>
                洗护方式：
                <el-tag
                  :type="r.wash_method === '手洗' ? 'success' : r.wash_method === '机洗' ? 'primary' : 'warning'"
                  effect="light"
                  size="small"
                >
                  {{ r.wash_method }}
                </el-tag>
              </p>
              <p v-if="r.detergent">洗涤剂：{{ r.detergent }}</p>
              <p v-if="r.deformation_after !== '无'">
                洗后变形：
                <el-tag :class="getDeformationClass(r.deformation_after)" size="small">
                  {{ r.deformation_after }}
                </el-tag>
              </p>
              <p v-if="r.notes">备注：{{ r.notes }}</p>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无洗护记录" />
        </el-tab-pane>

        <el-tab-pane label="出行占用" name="trip">
          <div v-if="detail.trip_occupancy && detail.trip_occupancy.length > 0" class="trip-section">
            <div class="trip-alert" v-if="hasInProgressTrip">
              <el-icon color="#e6a23c"><WarningFilled /></el-icon>
              <span>该衣物正在被出行计划占用，请确认是否可用</span>
            </div>
            <div class="trip-list">
              <div v-for="trip in detail.trip_occupancy" :key="trip.trip_id" class="trip-item">
                <div class="trip-item-header">
                  <span class="trip-name">{{ trip.trip_name }}</span>
                  <el-tag size="small" :type="getTripStatusType(trip.status)" effect="dark">
                    {{ trip.status }}
                  </el-tag>
                </div>
                <div class="trip-item-meta">
                  <span class="trip-meta-item">
                    <el-icon><LocationFilled /></el-icon>
                    {{ trip.destination }}
                  </span>
                  <span class="trip-meta-item">
                    <el-icon><Calendar /></el-icon>
                    {{ trip.start_date }} 至 {{ trip.end_date }}
                  </span>
                  <span class="trip-meta-item">
                    <el-icon><Box /></el-icon>
                    {{ trip.pack_status }}
                  </span>
                </div>
              </div>
            </div>
          </div>
          <el-empty v-else description="近期无出行占用" />
        </el-tab-pane>

        <el-tab-pane label="更换评估" name="replacement">
          <div v-if="detail.replacement_status" class="replacement-section">
            <el-progress
              :percentage="Math.min(100, Math.round(detail.replacement_status.overall_score * 100))"
              :color="getProgressColor(detail.replacement_status.urgency)"
              :stroke-width="12"
            />
            <div class="replacement-details">
              <div class="detail-grid">
                <div class="detail-item">
                  <div class="label">使用次数占比</div>
                  <div class="value" :class="{ danger: detail.replacement_status.use_ratio >= 0.9 }">
                    {{ Math.round(detail.replacement_status.use_ratio * 100) }}%
                  </div>
                </div>
                <div class="detail-item">
                  <div class="label">使用时长占比</div>
                  <div class="value" :class="{ danger: detail.replacement_status.time_ratio >= 0.9 }">
                    {{ Math.round(detail.replacement_status.time_ratio * 100) }}%
                  </div>
                </div>
                <div class="detail-item">
                  <div class="label">剩余使用次数</div>
                  <div class="value">{{ detail.replacement_status.uses_remaining }} 次</div>
                </div>
                <div class="detail-item">
                  <div class="label">剩余天数</div>
                  <div class="value">{{ detail.replacement_status.days_remaining }} 天</div>
                </div>
              </div>

              <div class="reasons-box" v-if="detail.replacement_status.reasons.length">
                <h4>评估原因</h4>
                <ul>
                  <li v-for="(r, i) in detail.replacement_status.reasons" :key="i">
                    <el-icon><CaretRight /></el-icon>
                    {{ r }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>

      <div class="drawer-actions">
        <el-button type="warning" @click="handleOpenWash">
          <el-icon><Brush /></el-icon>
          记录洗护
        </el-button>
        <el-button type="primary" @click="handleOpenWear">
          <el-icon><Calendar /></el-icon>
          记录穿着
        </el-button>
      </div>
    </div>

    <el-dialog v-model="washDialogVisible" title="记录洗护" width="480px" destroy-on-close>
      <el-form :model="washForm" label-width="100px" ref="washFormRef" :rules="washRules">
        <el-form-item label="衣物">
          <el-input :model-value="detail?.name" disabled />
        </el-form-item>
        <el-form-item label="洗护日期" prop="wash_date">
          <el-date-picker
            v-model="washForm.wash_date"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="洗护方式" prop="wash_method">
          <el-select v-model="washForm.wash_method" style="width: 100%">
            <el-option
              v-for="w in enums?.wash_methods"
              :key="w.value"
              :label="w.value"
              :value="w.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="洗涤剂">
          <el-input v-model="washForm.detergent" placeholder="如：蓝月亮洗衣液" />
        </el-form-item>
        <el-form-item label="洗后变形">
          <el-select v-model="washForm.deformation_after" style="width: 100%">
            <el-option
              v-for="d in enums?.deformation_levels"
              :key="d.value"
              :label="d.value"
              :value="d.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="washForm.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="washDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitWash">记录</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="wearDialogVisible" title="记录穿着" width="480px" destroy-on-close>
      <el-form :model="wearForm" label-width="100px" ref="wearFormRef" :rules="wearRules">
        <el-form-item label="衣物">
          <el-input :model-value="detail?.name" disabled />
        </el-form-item>
        <el-form-item label="穿着日期" prop="wear_date">
          <el-date-picker
            v-model="wearForm.wear_date"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="穿着时长">
          <el-input-number v-model="wearForm.duration_hours" :min="1" :max="24" /> 小时
        </el-form-item>
        <el-form-item label="变形情况">
          <el-select v-model="wearForm.deformation_noticed" style="width: 100%">
            <el-option
              v-for="d in enums?.deformation_levels"
              :key="d.value"
              :label="d.value"
              :value="d.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="wearForm.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="wearDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitWear">记录</el-button>
      </template>
    </el-dialog>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed, type FormInstance, type FormRules } from 'vue'
import { ElMessage } from 'element-plus'
import { garmentApi, enumApi, washRecordApi, wearRecordApi } from '@/api'
import type { GarmentDetail, Enums } from '@/types'
import {
  Loading, Box, Brush, Sunny, Document, Lightning, Timer,
  Calendar, Warning, WarningFilled, InfoFilled, CaretRight,
  Suitcase, LocationFilled
} from '@element-plus/icons-vue'

const props = defineProps<{
  garmentId: number | null
  visible: boolean
}>()

const emit = defineEmits(['update:visible', 'refresh'])

const drawerVisible = ref(false)
const loading = ref(false)
const detail = ref<GarmentDetail | null>(null)
const activeTab = ref('basic')
const enums = ref<Enums | null>(null)

const washDialogVisible = ref(false)
const wearDialogVisible = ref(false)
const washFormRef = ref<FormInstance>()
const wearFormRef = ref<FormInstance>()

const washForm = reactive({
  wash_date: new Date().toISOString().split('T')[0],
  wash_method: '手洗',
  detergent: '',
  deformation_after: '无',
  notes: ''
})

const wearForm = reactive({
  wear_date: new Date().toISOString().split('T')[0],
  duration_hours: 8,
  deformation_noticed: '无',
  notes: ''
})

const washRules: FormRules = {
  wash_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  wash_method: [{ required: true, message: '请选择洗护方式', trigger: 'change' }],
}

const wearRules: FormRules = {
  wear_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
}

watch(() => props.visible, (val) => {
  drawerVisible.value = val
  if (val && props.garmentId) {
    loadDetail()
  }
})

watch(drawerVisible, (val) => {
  emit('update:visible', val)
})

const loadDetail = async () => {
  if (!props.garmentId) return
  loading.value = true
  try {
    if (!enums.value) {
      enums.value = await enumApi.get()
    }
    detail.value = await garmentApi.getDetail(props.garmentId)
    if (detail.value.next_wash_plan && detail.value.next_wash_plan.overdue_days > 0) {
      activeTab.value = 'plan'
    }
  } catch (e) {
    ElMessage.error('加载详情失败')
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  detail.value = null
  activeTab.value = 'basic'
}

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

const getStatusClass = (urgency: string) => {
  if (urgency === '立即更换') return 'tag-urgent'
  if (urgency === '建议更换') return 'tag-warning'
  if (urgency === '注意观察') return 'tag-notice'
  return 'tag-good'
}

const getDeformationClass = (level: string) => {
  if (level === '严重' || level === '中度') return 'tag-urgent'
  if (level === '轻微') return 'tag-warning'
  return 'tag-good'
}

const getRiskClass = (risk: string) => {
  if (risk === '高风险') return 'tag-urgent'
  if (risk === '中风险') return 'tag-warning'
  if (risk === '低风险' || risk === '待处理') return 'tag-notice'
  return 'tag-good'
}

const getProgressColor = (urgency: string) => {
  if (urgency === '立即更换') return '#ef5350'
  if (urgency === '建议更换') return '#ffa726'
  return '#42a5f5'
}

const getTripStatusType = (status: string) => {
  const map: Record<string, string> = {
    '规划中': '',
    '打包中': 'warning',
    '出行中': 'primary',
    '已完成': 'success',
    '已取消': 'info'
  }
  return map[status] || ''
}

const hasInProgressTrip = computed(() => {
  if (!detail.value?.trip_occupancy) return false
  return detail.value.trip_occupancy.some(t => 
    t.status === '出行中' || t.status === '打包中'
  )
})

const handleOpenWash = () => {
  Object.assign(washForm, {
    wash_date: new Date().toISOString().split('T')[0],
    wash_method: detail?.next_wash_plan?.suggested_wash_method?.includes('手洗') ? '手洗' : '机洗',
    detergent: '',
    deformation_after: '无',
    notes: ''
  })
  washDialogVisible.value = true
}

const handleOpenWear = () => {
  Object.assign(wearForm, {
    wear_date: new Date().toISOString().split('T')[0],
    duration_hours: 8,
    deformation_noticed: '无',
    notes: ''
  })
  wearDialogVisible.value = true
}

const submitWash = async () => {
  if (!washFormRef.value || !detail.value) return
  await washFormRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      await washRecordApi.create({
        garment_id: detail.value!.id,
        ...washForm
      })
      ElMessage.success('洗护记录已添加')
      washDialogVisible.value = false
      await loadDetail()
      emit('refresh')
    } catch (e) {
      ElMessage.error('记录失败')
    }
  })
}

const submitWear = async () => {
  if (!wearFormRef.value || !detail.value) return
  await wearFormRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      await wearRecordApi.create({
        garment_id: detail.value!.id,
        ...wearForm
      })
      ElMessage.success('穿着记录已添加')
      wearDialogVisible.value = false
      await loadDetail()
      emit('refresh')
    } catch (e) {
      ElMessage.error('记录失败')
    }
  })
}
</script>

<style scoped>
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #8d6e63;
}

.detail-content {
  padding-right: 8px;
}

.garment-header {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.color-block {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  border: 2px solid rgba(0, 0, 0, 0.08);
  flex-shrink: 0;
}

.header-info h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
  color: #5d4037;
}

.tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.detail-tabs {
  margin-bottom: 20px;
}

.detail-tabs :deep(.el-tabs__content) {
  padding-top: 8px;
}

.sub-text {
  font-size: 12px;
  color: #a1887f;
  margin-left: 6px;
}

.danger {
  color: #ef4444;
  font-weight: 600;
}

.wash-plan-card {
  background: linear-gradient(135deg, #f3e5f5 0%, #e8eaf6 100%);
  border-radius: 12px;
  padding: 20px;
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.plan-date {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #5d4037;
  font-weight: 500;
}

.plan-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}

.metric .label {
  font-size: 12px;
  color: #8d6e63;
  margin-bottom: 4px;
}

.metric .value {
  font-size: 16px;
  font-weight: 600;
  color: #5d4037;
}

.trigger-reason {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 8px;
  padding: 10px 14px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  color: #5d4037;
  font-size: 13px;
  line-height: 1.5;
}

.trigger-reason .el-icon {
  margin-top: 2px;
  flex-shrink: 0;
  color: #7e57c2;
}

.replacement-section {
  padding: 4px 0;
}

.replacement-details {
  margin-top: 20px;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 20px;
}

.detail-item .label {
  font-size: 12px;
  color: #8d6e63;
  margin-bottom: 4px;
}

.detail-item .value {
  font-size: 18px;
  font-weight: 600;
  color: #5d4037;
}

.reasons-box {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
}

.reasons-box h4 {
  font-size: 14px;
  color: #8d6e63;
  margin: 0 0 12px 0;
}

.reasons-box ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.reasons-box li {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 13px;
  color: #5d4037;
  padding: 4px 0;
}

.drawer-actions {
  display: flex;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

:deep(.el-timeline-item__timestamp) {
  color: #8d6e63;
  font-weight: 500;
}

:deep(.el-timeline-item h4) {
  margin: 0 0 6px 0;
  font-size: 15px;
  color: #5d4037;
}

:deep(.el-timeline-item p) {
  margin: 4px 0;
  font-size: 13px;
  color: #8d6e63;
}

.trip-section {
  padding: 4px 0;
}

.trip-alert {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #fdf6ec;
  border: 1px solid #f5dab1;
  border-radius: 8px;
  margin-bottom: 16px;
  color: #e6a23c;
  font-size: 14px;
}

.trip-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.trip-item {
  padding: 16px;
  background: #fafafa;
  border-radius: 12px;
  border-left: 4px solid #ec407a;
}

.trip-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.trip-name {
  font-weight: 600;
  color: #5d4037;
  font-size: 15px;
}

.trip-item-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.trip-meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #8d6e63;
  font-size: 13px;
}

.trip-meta-item .el-icon {
  color: #ec407a;
}
</style>
