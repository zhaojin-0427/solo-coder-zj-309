<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon color="#2196f3"><Brush /></el-icon>
        洗护与穿着记录
      </h2>
      <div class="header-actions">
        <el-radio-group v-model="activeTab" size="large">
          <el-radio-button value="wash">洗护记录</el-radio-button>
          <el-radio-button value="wear">穿着记录</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <el-row :gutter="20" style="margin-bottom: 24px">
      <el-col :span="6">
        <div class="stats-card quick-stat">
          <div class="stat-icon" style="background: #e3f2fd;">
            <el-icon :size="24" color="#1976d2"><Brush /></el-icon>
          </div>
          <div>
            <div class="num">{{ totalWashes }}</div>
            <div class="label">总洗护次数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stats-card quick-stat">
          <div class="stat-icon" style="background: #fce4ec;">
            <el-icon :size="24" color="#c2185b"><Female /></el-icon>
          </div>
          <div>
            <div class="num">{{ totalWears }}</div>
            <div class="label">总穿着次数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stats-card quick-stat">
          <div class="stat-icon" style="background: #e8f5e9;">
            <el-icon :size="24" color="#388e3c"><Present /></el-icon>
          </div>
          <div>
            <div class="num">{{ washByMethod.hand || 0 }}</div>
            <div class="label">手洗次数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stats-card quick-stat">
          <div class="stat-icon" style="background: #fff3e0;">
            <el-icon :size="24" color="#f57c00"><Warning /></el-icon>
          </div>
          <div>
            <div class="num">{{ deformationCount }}</div>
            <div class="label">变形记录</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-card shadow="never" class="stats-card">
      <div class="filter-bar">
        <el-select
          v-model="filterGarmentId"
          placeholder="全部衣物"
          clearable
          style="width: 200px"
        >
          <el-option
            v-for="g in garments"
            :key="g.id"
            :label="g.name"
            :value="g.id"
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
        />
        <el-select
          v-if="activeTab === 'wash'"
          v-model="filterWashMethod"
          placeholder="全部洗护方式"
          clearable
          style="width: 140px"
        >
          <el-option label="机洗" value="机洗" />
          <el-option label="手洗" value="手洗" />
          <el-option label="干洗" value="干洗" />
        </el-select>
      </div>

      <div v-if="activeTab === 'wash'">
        <el-table
          :data="filteredWashRecords"
          v-loading="loading"
          stripe
          empty-text="暂无洗护记录"
        >
          <el-table-column label="洗护日期" width="130" sortable>
            <template #default="{ row }">
              <div class="date-cell">
                <el-icon><Calendar /></el-icon>
                {{ row.wash_date }}
              </div>
            </template>
          </el-table-column>
          <el-table-column label="衣物名称" min-width="200">
            <template #default="{ row }">
              <div class="garment-name">{{ row.garment_name }}</div>
            </template>
          </el-table-column>
          <el-table-column label="洗护方式" width="120">
            <template #default="{ row }">
              <el-tag
                :type="row.wash_method === '手洗' ? 'success' : row.wash_method === '机洗' ? 'primary' : 'warning'"
                effect="light"
              >
                {{ row.wash_method }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="洗涤剂" min-width="160">
            <template #default="{ row }">
              <span v-if="row.detergent">{{ row.detergent }}</span>
              <span v-else style="color: #bdbdbd">未记录</span>
            </template>
          </el-table-column>
          <el-table-column label="洗后变形" width="120">
            <template #default="{ row }">
              <el-tag
                v-if="row.deformation_after !== '无'"
                :class="getDeformationClass(row.deformation_after)"
              >
                {{ row.deformation_after }}
              </el-tag>
              <span v-else style="color: #4caf50">
                <el-icon><CircleCheck /></el-icon> 无
              </span>
            </template>
          </el-table-column>
          <el-table-column label="备注" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">
              <span v-if="row.notes">{{ row.notes }}</span>
              <span v-else style="color: #bdbdbd">-</span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div v-else>
        <el-table
          :data="filteredWearRecords"
          v-loading="loading"
          stripe
          empty-text="暂无穿着记录"
        >
          <el-table-column label="穿着日期" width="130" sortable>
            <template #default="{ row }">
              <div class="date-cell">
                <el-icon><Calendar /></el-icon>
                {{ row.wear_date }}
              </div>
            </template>
          </el-table-column>
          <el-table-column label="衣物名称" min-width="200">
            <template #default="{ row }">
              <div class="garment-name">{{ row.garment_name }}</div>
            </template>
          </el-table-column>
          <el-table-column label="穿着时长" width="120">
            <template #default="{ row }">
              <el-icon><Timer /></el-icon>
              {{ row.duration_hours }} 小时
            </template>
          </el-table-column>
          <el-table-column label="变形观察" width="120">
            <template #default="{ row }">
              <el-tag
                v-if="row.deformation_noticed !== '无'"
                :class="getDeformationClass(row.deformation_noticed)"
              >
                {{ row.deformation_noticed }}
              </el-tag>
              <span v-else style="color: #4caf50">
                <el-icon><CircleCheck /></el-icon> 无
              </span>
            </template>
          </el-table-column>
          <el-table-column label="备注" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">
              <span v-if="row.notes">{{ row.notes }}</span>
              <span v-else style="color: #bdbdbd">-</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { washRecordApi, wearRecordApi, garmentApi } from '@/api'
import type { WashRecord, WearRecord, Garment } from '@/types'
import { Brush, Female, Warning, Calendar, Timer, CircleCheck, Present } from '@element-plus/icons-vue'

const loading = ref(false)
const activeTab = ref('wash')
const washRecords = ref<WashRecord[]>([])
const wearRecords = ref<WearRecord[]>([])
const garments = ref<Garment[]>([])

const filterGarmentId = ref<number | null>(null)
const dateRange = ref<string[]>([])
const filterWashMethod = ref('')

const totalWashes = computed(() => washRecords.value.length)
const totalWears = computed(() => wearRecords.value.length)

const washByMethod = computed(() => {
  const result: Record<string, number> = {}
  for (const r of washRecords.value) {
    result[r.wash_method] = (result[r.wash_method] || 0) + 1
  }
  return result
})

const deformationCount = computed(() => {
  const wCount = washRecords.value.filter(r => r.deformation_after !== '无').length
  const wearCount = wearRecords.value.filter(r => r.deformation_noticed !== '无').length
  return wCount + wearCount
})

const filteredWashRecords = computed(() => {
  return washRecords.value.filter(r => {
    if (filterGarmentId.value && r.garment_id !== filterGarmentId.value) return false
    if (filterWashMethod.value && r.wash_method !== filterWashMethod.value) return false
    if (dateRange.value.length === 2) {
      if (r.wash_date < dateRange.value[0] || r.wash_date > dateRange.value[1]) return false
    }
    return true
  })
})

const filteredWearRecords = computed(() => {
  return wearRecords.value.filter(r => {
    if (filterGarmentId.value && r.garment_id !== filterGarmentId.value) return false
    if (dateRange.value.length === 2) {
      if (r.wear_date < dateRange.value[0] || r.wear_date > dateRange.value[1]) return false
    }
    return true
  })
})

const getDeformationClass = (level: string) => {
  if (level === '严重') return 'tag-urgent'
  if (level === '中度') return 'tag-warning'
  if (level === '轻微') return 'tag-notice'
  return 'tag-good'
}

const loadData = async () => {
  loading.value = true
  try {
    const [w, wr, g] = await Promise.all([
      washRecordApi.list(),
      wearRecordApi.list(),
      garmentApi.list({ is_active: 1 })
    ])
    washRecords.value = w
    wearRecords.value = wr
    garments.value = g
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.quick-stat {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  border-radius: 12px;
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quick-stat .num {
  font-size: 26px;
  font-weight: 700;
  color: #5d4037;
  line-height: 1;
}

.quick-stat .label {
  font-size: 13px;
  color: #8d6e63;
  margin-top: 4px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.date-cell {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
  color: #5d4037;
}

.garment-name {
  font-weight: 500;
  color: #5d4037;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>
