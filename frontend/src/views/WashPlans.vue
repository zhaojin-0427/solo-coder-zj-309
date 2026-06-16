<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon color="#9c27b0"><Calendar /></el-icon>
        洗护计划
      </h2>
      <div class="header-actions">
        <el-button type="primary" @click="loadData">
          <el-icon><Refresh /></el-icon>
          刷新计划
        </el-button>
      </div>
    </div>

    <el-row :gutter="20" style="margin-bottom: 24px">
      <el-col :span="6">
        <div class="kpi-card kpi-overdue" v-if="groupedData">
          <div class="kpi-icon">
            <el-icon :size="28"><Warning /></el-icon>
          </div>
          <div>
            <div class="kpi-value">{{ groupedData.overdue.length }}</div>
            <div class="kpi-label">已逾期</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="kpi-card kpi-today" v-if="groupedData">
          <div class="kpi-icon">
            <el-icon :size="28"><Bell /></el-icon>
          </div>
          <div>
            <div class="kpi-value">{{ groupedData.today.length }}</div>
            <div class="kpi-label">今日待处理</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="kpi-card kpi-week" v-if="groupedData">
          <div class="kpi-icon">
            <el-icon :size="28"><Calendar /></el-icon>
          </div>
          <div>
            <div class="kpi-value">{{ groupedData.next_7_days.length }}</div>
            <div class="kpi-label">未来7天</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="kpi-card kpi-total">
          <div class="kpi-icon">
            <el-icon :size="28"><Brush /></el-icon>
          </div>
          <div>
            <div class="kpi-value">{{ totalPlanned }}</div>
            <div class="kpi-label">待洗护总数</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-card shadow="never" class="stats-card" style="margin-bottom: 24px">
      <div class="filter-bar">
        <el-select
          v-model="filterRisk"
          placeholder="全部风险等级"
          clearable
          style="width: 160px"
          @change="loadData"
        >
          <el-option label="高风险" value="高风险" />
          <el-option label="中风险" value="中风险" />
          <el-option label="低风险" value="低风险" />
          <el-option label="待处理" value="待处理" />
          <el-option label="正常" value="正常" />
        </el-select>
        <el-select
          v-model="filterZone"
          placeholder="全部收纳区"
          clearable
          style="width: 160px"
          @change="loadData"
        >
          <el-option
            v-for="zone in storageZones"
            :key="zone.id"
            :label="zone.name"
            :value="zone.id"
          />
        </el-select>
        <el-select
          v-model="filterFabric"
          placeholder="全部面料"
          clearable
          style="width: 140px"
          @change="loadData"
        >
          <el-option
            v-for="f in enums?.fabrics"
            :key="f.value"
            :label="f.value"
            :value="f.value"
          />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          style="width: 280px"
          @change="loadData"
        />
      </div>
    </el-card>

    <div v-if="groupedData && loading" class="loading-container">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <p style="margin-top: 12px; color: #8d6e63;">加载中...</p>
    </div>

    <div v-else-if="groupedData">
      <section v-if="groupedData.overdue.length > 0" class="plan-section">
        <div class="section-header">
          <h3 class="section-title">
            <el-icon color="#ef5350"><Warning /></el-icon>
            已逾期
            <el-tag type="danger" effect="light" style="margin-left: 8px">
              {{ groupedData.overdue.length }} 件
            </el-tag>
          </h3>
        </div>
        <el-row :gutter="20">
          <el-col :span="8" v-for="plan in groupedData.overdue" :key="plan.garment.id">
            <PlanCard
              :plan="plan"
              @open-detail="openDetail(plan.garment.id)"
              @record-wash="openWashDialog(plan)"
            />
          </el-col>
        </el-row>
      </section>

      <section v-if="groupedData.today.length > 0" class="plan-section">
        <div class="section-header">
          <h3 class="section-title">
            <el-icon color="#f57c00"><Bell /></el-icon>
            今日待处理
            <el-tag type="warning" effect="light" style="margin-left: 8px">
              {{ groupedData.today.length }} 件
            </el-tag>
          </h3>
        </div>
        <el-row :gutter="20">
          <el-col :span="8" v-for="plan in groupedData.today" :key="plan.garment.id">
            <PlanCard
              :plan="plan"
              @open-detail="openDetail(plan.garment.id)"
              @record-wash="openWashDialog(plan)"
            />
          </el-col>
        </el-row>
      </section>

      <section v-if="groupedData.next_7_days.length > 0" class="plan-section">
        <div class="section-header">
          <h3 class="section-title">
            <el-icon color="#1976d2"><Calendar /></el-icon>
            未来 7 天
            <el-tag type="primary" effect="light" style="margin-left: 8px">
              {{ groupedData.next_7_days.length }} 件
            </el-tag>
          </h3>
        </div>
        <el-row :gutter="20">
          <el-col :span="8" v-for="plan in groupedData.next_7_days" :key="plan.garment.id">
            <PlanCard
              :plan="plan"
              @open-detail="openDetail(plan.garment.id)"
              @record-wash="openWashDialog(plan)"
            />
          </el-col>
        </el-row>
      </section>

      <div
        v-if="!groupedData.overdue.length && !groupedData.today.length && !groupedData.next_7_days.length"
        class="empty-container"
      >
        <el-card shadow="never" class="stats-card empty-card">
          <div class="empty-state">
            <el-icon color="#66bb6a"><CircleCheckFilled /></el-icon>
            <h3>太棒了！</h3>
            <p>{{ filterRisk || filterZone || filterFabric || dateRange ? '当前筛选条件下没有待处理的洗护计划' : '所有衣物洗护计划已完成，暂无待处理' }}</p>
            <p style="margin-top: 8px; font-size: 13px; color: #a1887f">
              系统会根据穿着次数、洗护间隔和面料特性自动计算洗护计划
            </p>
          </div>
        </el-card>
      </div>
    </div>

    <GarmentDetailDrawer
      v-model:visible="drawerVisible"
      :garment-id="selectedGarmentId"
      @refresh="onDrawerRefresh"
    />

    <el-dialog
      v-model="washDialogVisible"
      title="记录洗护"
      width="480px"
      destroy-on-close
    >
      <el-form :model="washForm" label-width="100px" ref="washFormRef" :rules="washRules">
        <el-form-item label="衣物">
          <el-input :model-value="selectedPlan?.garment.name" disabled />
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, type FormInstance, type FormRules, defineAsyncComponent } from 'vue'
import { ElMessage } from 'element-plus'
import {
  washPlanApi, storageZoneApi, enumApi, washRecordApi
} from '@/api'
import type {
  WashPlan, PlanGroupResponse, StorageZone, Enums
} from '@/types'
import {
  Calendar, Refresh, Warning, Bell, Brush, Loading,
  CircleCheckFilled
} from '@element-plus/icons-vue'

const emit = defineEmits(['refresh-reminders', 'refresh-wash-plans'])

const GarmentDetailDrawer = defineAsyncComponent(() => import('@/components/GarmentDetailDrawer.vue'))
const PlanCard = defineAsyncComponent(() => import('@/components/PlanCard.vue'))

const loading = ref(false)
const groupedData = ref<PlanGroupResponse | null>(null)
const storageZones = ref<StorageZone[]>([])
const enums = ref<Enums | null>(null)

const filterRisk = ref('')
const filterZone = ref<number | null>(null)
const filterFabric = ref('')
const dateRange = ref<string[]>([])

const drawerVisible = ref(false)
const selectedGarmentId = ref<number | null>(null)

const washDialogVisible = ref(false)
const washFormRef = ref<FormInstance>()
const selectedPlan = ref<WashPlan | null>(null)
const washForm = reactive({
  wash_date: new Date().toISOString().split('T')[0],
  wash_method: '手洗',
  detergent: '',
  deformation_after: '无',
  notes: ''
})

const washRules: FormRules = {
  wash_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  wash_method: [{ required: true, message: '请选择洗护方式', trigger: 'change' }],
}

const totalPlanned = computed(() => {
  if (!groupedData.value) return 0
  return groupedData.value.overdue.length + groupedData.value.today.length + groupedData.value.next_7_days.length
})

const loadData = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (filterRisk.value) params.risk_level = filterRisk.value
    if (filterZone.value !== null) params.storage_zone_id = filterZone.value
    if (filterFabric.value) params.fabric = filterFabric.value
    if (dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }

    if (!enums.value) {
      enums.value = await enumApi.get()
    }
    if (!storageZones.value.length) {
      storageZones.value = await storageZoneApi.list()
    }

    if (Object.keys(params).length > 0) {
      const allPlans = await washPlanApi.list(params)
      const today = new Date().toISOString().split('T')[0]
      const sevenDaysLater = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]

      const overdue: WashPlan[] = []
      const todayList: WashPlan[] = []
      const next7Days: WashPlan[] = []

      for (const plan of allPlans) {
        if (plan.overdue_days > 0) {
          overdue.push(plan)
        } else if (plan.suggested_wash_date === today) {
          todayList.push(plan)
        } else if (plan.suggested_wash_date <= sevenDaysLater) {
          next7Days.push(plan)
        }
      }

      const sortKey = (p: WashPlan) => [p.overdue_days, p.suggested_wash_date]
      overdue.sort((a, b) => sortKey(b)[0] - sortKey(a)[0])
      todayList.sort((a, b) => a.suggested_wash_date.localeCompare(b.suggested_wash_date))
      next7Days.sort((a, b) => a.suggested_wash_date.localeCompare(b.suggested_wash_date))

      groupedData.value = {
        overdue,
        today: todayList,
        next_7_days: next7Days,
      }
    } else {
      groupedData.value = await washPlanApi.grouped()
    }

    emit('refresh-reminders')
  } catch (e) {
    ElMessage.error('加载洗护计划失败')
  } finally {
    loading.value = false
  }
}

const openDetail = (garmentId: number) => {
  selectedGarmentId.value = garmentId
  drawerVisible.value = true
}

const openWashDialog = (plan: WashPlan) => {
  selectedPlan.value = plan
  Object.assign(washForm, {
    wash_date: new Date().toISOString().split('T')[0],
    wash_method: plan.suggested_wash_method.includes('手洗') ? '手洗' : plan.suggested_wash_method.includes('干洗') ? '干洗' : '机洗',
    detergent: '',
    deformation_after: '无',
    notes: ''
  })
  washDialogVisible.value = true
}

const submitWash = async () => {
  if (!washFormRef.value || !selectedPlan.value) return
  await washFormRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      await washRecordApi.create({
        garment_id: selectedPlan.value!.garment.id,
        ...washForm
      })
      ElMessage.success('洗护记录已添加')
      washDialogVisible.value = false
      await loadData()
      emit('refresh-reminders')
      emit('refresh-wash-plans')
    } catch (e) {
      ElMessage.error('记录失败')
    }
  })
}

const onDrawerRefresh = async () => {
  await loadData()
  emit('refresh-reminders')
  emit('refresh-wash-plans')
}

onMounted(loadData)
</script>

<style scoped>
.kpi-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  border-radius: 16px;
  color: white;
  position: relative;
  overflow: hidden;
}

.kpi-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.kpi-overdue { background: linear-gradient(135deg, #ef5350, #e57373); }
.kpi-today { background: linear-gradient(135deg, #ff9800, #ffb74d); }
.kpi-week { background: linear-gradient(135deg, #42a5f5, #64b5f6); }
.kpi-total { background: linear-gradient(135deg, #9c27b0, #ba68c8); }

.kpi-icon {
  width: 56px;
  height: 56px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
}

.kpi-value {
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
}

.kpi-label {
  font-size: 14px;
  opacity: 0.9;
  margin-top: 6px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #8d6e63;
}

.plan-section {
  margin-bottom: 32px;
}

.section-header {
  margin-bottom: 16px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #5d4037;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
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
