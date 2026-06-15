<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon color="#ec407a"><Female /></el-icon>
        衣物档案
      </h2>
      <el-button type="primary" @click="openCreateDialog" size="large">
        <el-icon><Plus /></el-icon>
        新建衣物
      </el-button>
    </div>

    <el-card shadow="never" class="stats-card" style="margin-bottom: 24px">
      <el-row :gutter="24">
        <el-col :span="6">
          <div class="stat-item">
            <el-icon :size="32" color="#ec407a"><Female /></el-icon>
            <div>
              <p class="stat-value">{{ garments.length }}</p>
              <p class="stat-label">衣物总数</p>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <el-icon :size="32" color="#ff9800"><Goods /></el-icon>
            <div>
              <p class="stat-value">{{ categoryCount }}</p>
              <p class="stat-label">品类数量</p>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <el-icon :size="32" color="#9c27b0"><EditPen /></el-icon>
            <div>
              <p class="stat-value">{{ fabricCount }}</p>
              <p class="stat-label">面料种类</p>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <el-icon :size="32" color="#4caf50"><Star /></el-icon>
            <div>
              <p class="stat-value">{{ totalUseCount }}</p>
              <p class="stat-label">累计使用次数</p>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-card shadow="never" class="stats-card">
      <div class="filter-bar">
        <el-select
          v-model="filterCategory"
          placeholder="全部品类"
          clearable
          style="width: 140px"
          @change="filterGarments"
        >
          <el-option
            v-for="cat in enums?.categories"
            :key="cat.value"
            :label="cat.value"
            :value="cat.value"
          />
        </el-select>
        <el-select
          v-model="filterFabric"
          placeholder="全部面料"
          clearable
          style="width: 140px"
          @change="filterGarments"
        >
          <el-option
            v-for="f in enums?.fabrics"
            :key="f.value"
            :label="f.value"
            :value="f.value"
          />
        </el-select>
        <el-select
          v-model="filterZone"
          placeholder="全部收纳区"
          clearable
          style="width: 160px"
          @change="filterGarments"
        >
          <el-option
            v-for="zone in storageZones"
            :key="zone.id"
            :label="zone.name"
            :value="zone.id"
          />
        </el-select>
        <el-input
          v-model="searchText"
          placeholder="搜索衣物名称..."
          clearable
          style="width: 240px"
          :prefix-icon="Search"
          @input="filterGarments"
        />
      </div>

      <el-table
        :data="filteredGarments"
        v-loading="loading"
        stripe
        style="width: 100%"
        empty-text="暂无衣物，点击右上角新建"
      >
        <el-table-column label="衣物" min-width="200">
          <template #default="{ row }">
            <div class="garment-info">
              <div
                class="garment-color"
                :style="{ background: getColorCode(row.color) }"
              ></div>
              <div>
                <div class="garment-name">{{ row.name }}</div>
                <div class="garment-sub">
                  <el-tag size="small" type="info" effect="plain">{{ row.category }}</el-tag>
                  <span style="margin-left: 8px">{{ row.size }}</span>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="面料" width="120">
          <template #default="{ row }">
            <el-tag :type="getFabricTagType(row.fabric)" effect="light">
              {{ row.fabric }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="收纳位置" width="140">
          <template #default="{ row }">
            <span v-if="row.storage_zone">
              <el-icon><Box /></el-icon> {{ row.storage_zone.name }}
            </span>
            <span v-else style="color: #9e9e9e">未分区</span>
          </template>
        </el-table-column>
        <el-table-column label="使用/洗护" width="120" align="center">
          <template #default="{ row }">
            <div>{{ row.use_count }} 次 / {{ row.wash_count }} 次</div>
          </template>
        </el-table-column>
        <el-table-column label="购买日期" width="120">
          <template #default="{ row }">{{ row.purchase_date }}</template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag
              v-if="row.replacement_status"
              :class="getStatusClass(row.replacement_status.urgency)"
            >
              {{ row.replacement_status.urgency }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="openCareDialog(row)">
              <el-icon><Reading /></el-icon> 洗护建议
            </el-button>
            <el-button size="small" type="success" link @click="openWearDialog(row)">
              <el-icon><Calendar /></el-icon> 穿着
            </el-button>
            <el-button size="small" type="warning" link @click="openWashDialog(row)">
              <el-icon><Brush /></el-icon> 洗护
            </el-button>
            <el-button size="small" type="primary" link @click="openEditDialog(row)">编辑</el-button>
            <el-popconfirm
              title="确认停用此衣物？"
              @confirm="deleteGarment(row.id)"
            >
              <template #reference>
                <el-button size="small" type="danger" link>停用</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑衣物' : '新建衣物'"
      width="680px"
      destroy-on-close
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="衣物名称" prop="name">
              <el-input v-model="form.name" placeholder="如：粉色蕾丝文胸" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="品类" prop="category">
              <el-select v-model="form.category" placeholder="请选择" style="width: 100%">
                <el-option
                  v-for="cat in enums?.categories"
                  :key="cat.value"
                  :label="cat.value"
                  :value="cat.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="尺码" prop="size">
              <el-input v-model="form.size" placeholder="如：75B / M / L" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="颜色" prop="color">
              <el-input v-model="form.color" placeholder="如：粉色、黑色" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="面料" prop="fabric">
              <el-select v-model="form.fabric" placeholder="请选择" style="width: 100%" @change="onFabricChange">
                <el-option
                  v-for="f in enums?.fabrics"
                  :key="f.value"
                  :label="f.value"
                  :value="f.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="购买日期" prop="purchase_date">
              <el-date-picker
                v-model="form.purchase_date"
                type="date"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="收纳分区" prop="storage_zone_id">
              <el-select
                v-model="form.storage_zone_id"
                placeholder="请选择"
                clearable
                style="width: 100%"
              >
                <el-option
                  v-for="zone in storageZones"
                  :key="zone.id"
                  :label="`${zone.name} (${zone.current_count}/${zone.capacity})`"
                  :value="zone.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="品牌">
              <el-input v-model="form.brand" placeholder="选填" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="价格">
              <el-input-number v-model="form.price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="备注">
              <el-input v-model="form.notes" type="textarea" :rows="2" placeholder="选填" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-alert
          v-if="form.fabric && fabricAdvice"
          :title="`${form.fabric}面料洗护提示：${fabricAdvice.wash_method}，${fabricAdvice.notes}`"
          type="info"
          show-icon
          :closable="false"
          style="margin-bottom: 0"
        />
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="careDialogVisible" title="洗护建议" width="560px">
      <div v-if="currentGarment?.care_advice" class="care-advice">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="面料">
            <el-tag :type="getFabricTagType(currentGarment.fabric)">{{ currentGarment.fabric }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="洗涤方式">
            <el-icon><Brush /></el-icon>
            {{ currentGarment.care_advice.wash_method }}
          </el-descriptions-item>
          <el-descriptions-item label="水温要求">
            <el-icon><Sunny /></el-icon>
            {{ currentGarment.care_advice.wash_temp }}
          </el-descriptions-item>
          <el-descriptions-item label="晾晒方式">
            <el-icon><Sunny /></el-icon>
            {{ currentGarment.care_advice.drying }}
          </el-descriptions-item>
          <el-descriptions-item label="洗涤剂">
            <el-icon><Document /></el-icon>
            {{ currentGarment.care_advice.detergent }}
          </el-descriptions-item>
          <el-descriptions-item label="熨烫">
            <el-icon><Lightning /></el-icon>
            {{ currentGarment.care_advice.iron }}
          </el-descriptions-item>
          <el-descriptions-item label="推荐使用次数">
            <el-icon><Timer /></el-icon>
            {{ currentGarment.care_advice.recommended_uses }} 次
          </el-descriptions-item>
          <el-descriptions-item label="建议更换周期">
            <el-icon><Calendar /></el-icon>
            {{ currentGarment.care_advice.replacement_months }} 个月
          </el-descriptions-item>
          <el-descriptions-item label="注意事项">
            <el-icon><Warning /></el-icon>
            {{ currentGarment.care_advice.notes }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <el-dialog v-model="wearDialogVisible" title="记录穿着" width="480px">
      <el-form :model="wearForm" label-width="100px" ref="wearFormRef" :rules="wearRules">
        <el-form-item label="衣物">
          <el-input :model-value="currentGarment?.name" disabled />
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

    <el-dialog v-model="washDialogVisible" title="记录洗护" width="480px">
      <el-form :model="washForm" label-width="100px" ref="washFormRef" :rules="washRules">
        <el-form-item label="衣物">
          <el-input :model-value="currentGarment?.name" disabled />
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
import { ref, computed, onMounted, reactive } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import {
  garmentApi, storageZoneApi, enumApi, careAdviceApi,
  wearRecordApi, washRecordApi
} from '@/api'
import type { Garment, Enums, StorageZone, CareAdvice } from '@/types'
import { Search, Reading, Calendar, Brush, Plus, Female, Goods, EditPen, Star, Box, Sunny, Document, Lightning, Timer, Warning } from '@element-plus/icons-vue'

const emit = defineEmits(['refresh-reminders'])

const loading = ref(false)
const garments = ref<Garment[]>([])
const storageZones = ref<StorageZone[]>([])
const enums = ref<Enums | null>(null)
const filterCategory = ref('')
const filterFabric = ref('')
const filterZone = ref<number | null>(null)
const searchText = ref('')

const dialogVisible = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()
const form = reactive<any>({
  name: '',
  category: '',
  size: '',
  color: '',
  fabric: '',
  purchase_date: '',
  storage_zone_id: null,
  brand: '',
  price: 0,
  notes: ''
})
const fabricAdvice = ref<CareAdvice | null>(null)

const rules: FormRules = {
  name: [{ required: true, message: '请输入衣物名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择品类', trigger: 'change' }],
  size: [{ required: true, message: '请输入尺码', trigger: 'blur' }],
  color: [{ required: true, message: '请输入颜色', trigger: 'blur' }],
  fabric: [{ required: true, message: '请选择面料', trigger: 'change' }],
  purchase_date: [{ required: true, message: '请选择购买日期', trigger: 'change' }],
}

const careDialogVisible = ref(false)
const wearDialogVisible = ref(false)
const washDialogVisible = ref(false)
const currentGarment = ref<Garment | null>(null)

const wearFormRef = ref<FormInstance>()
const wearForm = reactive({
  wear_date: new Date().toISOString().split('T')[0],
  duration_hours: 8,
  deformation_noticed: '无',
  notes: ''
})
const wearRules: FormRules = {
  wear_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
}

const washFormRef = ref<FormInstance>()
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

const categoryCount = computed(() => {
  const s = new Set(garments.value.map(g => g.category))
  return s.size
})

const fabricCount = computed(() => {
  const s = new Set(garments.value.map(g => g.fabric))
  return s.size
})

const totalUseCount = computed(() => {
  return garments.value.reduce((sum, g) => sum + g.use_count, 0)
})

const filteredGarments = computed(() => {
  return garments.value.filter(g => {
    if (filterCategory.value && g.category !== filterCategory.value) return false
    if (filterFabric.value && g.fabric !== filterFabric.value) return false
    if (filterZone.value !== null && g.storage_zone_id !== filterZone.value) return false
    if (searchText.value && !g.name.includes(searchText.value)) return false
    return true
  })
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

const loadData = async () => {
  loading.value = true
  try {
    const [g, z, e] = await Promise.all([
      garmentApi.list({ is_active: 1 }),
      storageZoneApi.list(),
      enumApi.get()
    ])
    garments.value = g
    storageZones.value = z
    enums.value = e
  } catch (e: any) {
    ElMessage.error('加载失败：' + (e.message || ''))
  } finally {
    loading.value = false
  }
}

const filterGarments = () => {}

const resetForm = () => {
  Object.assign(form, {
    name: '', category: '', size: '', color: '', fabric: '',
    purchase_date: '', storage_zone_id: null, brand: '', price: 0, notes: ''
  })
  fabricAdvice.value = null
  formRef.value?.resetFields()
}

const openCreateDialog = () => {
  resetForm()
  isEditing.value = false
  editingId.value = null
  form.purchase_date = new Date().toISOString().split('T')[0]
  dialogVisible.value = true
}

const openEditDialog = (row: Garment) => {
  resetForm()
  isEditing.value = true
  editingId.value = row.id
  Object.assign(form, {
    name: row.name, category: row.category, size: row.size, color: row.color,
    fabric: row.fabric, purchase_date: row.purchase_date,
    storage_zone_id: row.storage_zone_id, brand: row.brand,
    price: row.price, notes: row.notes
  })
  onFabricChange()
  dialogVisible.value = true
}

const onFabricChange = async () => {
  if (form.fabric) {
    try {
      fabricAdvice.value = await careAdviceApi.get(form.fabric)
    } catch {
      fabricAdvice.value = null
    }
  } else {
    fabricAdvice.value = null
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      if (isEditing.value && editingId.value) {
        await garmentApi.update(editingId.value, form)
        ElMessage.success('更新成功')
      } else {
        await garmentApi.create(form)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      await loadData()
      emit('refresh-reminders')
    } catch (e: any) {
      ElMessage.error('操作失败：' + (e?.response?.data?.detail || e.message || ''))
    }
  })
}

const deleteGarment = async (id: number) => {
  try {
    await garmentApi.delete(id)
    ElMessage.success('已停用')
    await loadData()
    emit('refresh-reminders')
  } catch (e: any) {
    ElMessage.error('操作失败')
  }
}

const openCareDialog = (row: Garment) => {
  currentGarment.value = row
  careDialogVisible.value = true
}

const openWearDialog = (row: Garment) => {
  currentGarment.value = row
  Object.assign(wearForm, {
    wear_date: new Date().toISOString().split('T')[0],
    duration_hours: 8,
    deformation_noticed: '无',
    notes: ''
  })
  wearDialogVisible.value = true
}

const openWashDialog = (row: Garment) => {
  currentGarment.value = row
  Object.assign(washForm, {
    wash_date: new Date().toISOString().split('T')[0],
    wash_method: '手洗',
    detergent: '',
    deformation_after: '无',
    notes: ''
  })
  washDialogVisible.value = true
}

const submitWear = async () => {
  if (!wearFormRef.value || !currentGarment.value) return
  await wearFormRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      await wearRecordApi.create({
        garment_id: currentGarment.value!.id,
        ...wearForm
      })
      ElMessage.success('穿着记录已添加')
      wearDialogVisible.value = false
      await loadData()
    } catch (e: any) {
      ElMessage.error('记录失败')
    }
  })
}

const submitWash = async () => {
  if (!washFormRef.value || !currentGarment.value) return
  await washFormRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      await washRecordApi.create({
        garment_id: currentGarment.value!.id,
        ...washForm
      })
      ElMessage.success('洗护记录已添加')
      washDialogVisible.value = false
      await loadData()
      emit('refresh-reminders')
    } catch (e: any) {
      ElMessage.error('记录失败')
    }
  })
}

onMounted(loadData)
</script>

<style scoped>
.garment-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.garment-color {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  border: 2px solid #e0e0e0;
  flex-shrink: 0;
}

.garment-name {
  font-weight: 600;
  color: #5d4037;
}

.garment-sub {
  margin-top: 4px;
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #8d6e63;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #5d4037;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #8d6e63;
  margin-top: 4px;
}

.care-advice :deep(.el-descriptions__label) {
  width: 120px;
}
</style>
