<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon color="#ab47bc"><Box /></el-icon>
        收纳分区
      </h2>
      <el-button type="primary" @click="openCreateDialog" size="large">
        <el-icon><Plus /></el-icon>
        新建分区
      </el-button>
    </div>

    <el-row :gutter="20">
      <el-col :span="8" v-for="zone in storageZones" :key="zone.id">
        <el-card shadow="hover" class="zone-card card-hover">
          <div class="zone-header">
            <div class="zone-icon">
              <el-icon :size="28" :color="getZoneColor(zone.id)"><Box /></el-icon>
            </div>
            <div class="zone-info">
              <h3>{{ zone.name }}</h3>
              <p>{{ zone.description || '暂无描述' }}</p>
            </div>
          </div>

          <el-progress
            :percentage="Math.round(zone.current_count / zone.capacity * 100)"
            :color="getProgressColor(zone.current_count / zone.capacity)"
            style="margin: 20px 0"
          />

          <div class="zone-stats">
            <div class="stat-box">
              <div class="num">{{ zone.current_count }}</div>
              <div class="label">已收纳</div>
            </div>
            <div class="divider"></div>
            <div class="stat-box">
              <div class="num">{{ zone.capacity }}</div>
              <div class="label">容量</div>
            </div>
            <div class="divider"></div>
            <div class="stat-box">
              <div class="num">{{ Math.max(0, zone.capacity - zone.current_count) }}</div>
              <div class="label">空余</div>
            </div>
          </div>

          <div class="zone-garments" v-if="getZoneGarments(zone.id).length > 0">
            <el-divider content-position="left">
              <span style="font-weight: 600; color: #5d4037">已收纳衣物</span>
            </el-divider>
            <div class="garment-tags">
              <el-tag
                v-for="g in getZoneGarments(zone.id).slice(0, 8)"
                :key="g.id"
                size="small"
                effect="light"
                class="garment-tag"
                @click="viewGarment(g)"
              >
                <span
                  class="color-dot"
                  :style="{ background: getColorCode(g.color) }"
                ></span>
                {{ g.name }}
              </el-tag>
              <el-tag
                v-if="getZoneGarments(zone.id).length > 8"
                size="small"
                type="info"
              >
                +{{ getZoneGarments(zone.id).length - 8 }} 更多
              </el-tag>
            </div>
          </div>

          <div class="zone-actions">
            <el-button type="primary" link @click="viewZoneDetail(zone)">
              <el-icon><View /></el-icon> 详情
            </el-button>
            <el-button type="primary" link @click="openEditDialog(zone)">
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-popconfirm
              title="确认删除此分区？关联衣物将变为未分区状态"
              @confirm="deleteZone(zone.id)"
            >
              <template #reference>
                <el-button type="danger" link>
                  <el-icon><Delete /></el-icon> 删除
                </el-button>
              </template>
            </el-popconfirm>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8" v-if="storageZones.length === 0">
        <el-card class="zone-card empty-zone-card">
          <div class="empty-state">
            <el-icon><Box /></el-icon>
            <p>还没有创建收纳分区</p>
            <el-button type="primary" style="margin-top: 16px" @click="openCreateDialog">
              创建第一个分区
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑分区' : '新建分区'"
      width="480px"
      destroy-on-close
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="分区名称" prop="name">
          <el-input v-model="form.name" placeholder="如：抽屉A层、衣柜左格" />
        </el-form-item>
        <el-form-item label="容量" prop="capacity">
          <el-input-number v-model="form.capacity" :min="1" :max="100" style="width: 100%" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="选填，描述这个分区的位置或用途"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailVisible" :title="currentZone?.name || '分区详情'" width="680px">
      <div v-if="currentZone" class="zone-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="分区名称">{{ currentZone.name }}</el-descriptions-item>
          <el-descriptions-item label="容量">{{ currentZone.capacity }} 件</el-descriptions-item>
          <el-descriptions-item label="已收纳">{{ currentZone.current_count }} 件</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(currentZone.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ currentZone.description || '暂无描述' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">
          <span style="font-weight: 600; color: #5d4037">分区内衣物 ({{ getZoneGarments(currentZone.id).length }})</span>
        </el-divider>

        <el-table :data="getZoneGarments(currentZone.id)" size="small">
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="category" label="品类" width="100" />
          <el-table-column label="颜色" width="100">
            <template #default="{ row }">
              <span class="inline-color">
                <span
                  class="color-dot"
                  :style="{ background: getColorCode(row.color) }"
                ></span>
                {{ row.color }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="fabric" label="面料" width="100" />
          <el-table-column label="使用次数" width="100" align="center">
            <template #default="{ row }">{{ row.use_count }}</template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { storageZoneApi, garmentApi } from '@/api'
import type { StorageZone, Garment } from '@/types'
import { Plus, Box, Edit, Delete, View } from '@element-plus/icons-vue'

const storageZones = ref<StorageZone[]>([])
const garments = ref<Garment[]>([])

const dialogVisible = ref(false)
const detailVisible = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)
const currentZone = ref<StorageZone | null>(null)

const formRef = ref<FormInstance>()
const form = reactive({
  name: '',
  capacity: 10,
  description: ''
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入分区名称', trigger: 'blur' }],
  capacity: [{ required: true, message: '请输入容量', trigger: 'blur' }],
}

const zoneColors = ['#ec407a', '#ab47bc', '#7e57c2', '#5c6bc0', '#42a5f5', '#26c6da', '#66bb6a', '#ffa726', '#ef5350', '#8d6e63']

const getZoneColor = (id: number) => zoneColors[id % zoneColors.length]

const getProgressColor = (ratio: number) => {
  if (ratio >= 0.9) return '#ef5350'
  if (ratio >= 0.7) return '#ffa726'
  return '#66bb6a'
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

const getZoneGarments = (zoneId: number) => {
  return garments.value.filter(g => g.storage_zone_id === zoneId)
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const loadData = async () => {
  try {
    const [z, g] = await Promise.all([
      storageZoneApi.list(),
      garmentApi.list({ is_active: 1 })
    ])
    storageZones.value = z
    garments.value = g
  } catch (e) {
    ElMessage.error('加载失败')
  }
}

const resetForm = () => {
  Object.assign(form, { name: '', capacity: 10, description: '' })
  formRef.value?.resetFields()
}

const openCreateDialog = () => {
  resetForm()
  isEditing.value = false
  editingId.value = null
  dialogVisible.value = true
}

const openEditDialog = (zone: StorageZone) => {
  resetForm()
  isEditing.value = true
  editingId.value = zone.id
  Object.assign(form, {
    name: zone.name,
    capacity: zone.capacity,
    description: zone.description
  })
  dialogVisible.value = true
}

const viewZoneDetail = (zone: StorageZone) => {
  currentZone.value = zone
  detailVisible.value = true
}

const viewGarment = (_garment: Garment) => {
  ElMessage.info('请前往衣物档案页查看详情')
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      if (isEditing.value && editingId.value) {
        await storageZoneApi.update(editingId.value, form)
        ElMessage.success('更新成功')
      } else {
        await storageZoneApi.create(form)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      await loadData()
    } catch (e: any) {
      ElMessage.error('操作失败：' + (e?.response?.data?.detail || ''))
    }
  })
}

const deleteZone = async (id: number) => {
  try {
    await storageZoneApi.delete(id)
    ElMessage.success('已删除')
    await loadData()
  } catch {
    ElMessage.error('删除失败')
  }
}

onMounted(loadData)
</script>

<style scoped>
.zone-card {
  margin-bottom: 20px;
  border-radius: 16px;
  border: 1px solid #f5f5f5;
}

.empty-zone-card {
  min-height: 200px;
}

.zone-header {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.zone-icon {
  width: 56px;
  height: 56px;
  background: #fce4ec;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.zone-info h3 {
  font-size: 18px;
  font-weight: 600;
  color: #5d4037;
  margin: 0 0 6px 0;
}

.zone-info p {
  font-size: 13px;
  color: #8d6e63;
  margin: 0;
  line-height: 1.5;
}

.zone-stats {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
}

.stat-box {
  flex: 1;
  text-align: center;
}

.stat-box .num {
  font-size: 24px;
  font-weight: 700;
  color: #5d4037;
}

.stat-box .label {
  font-size: 12px;
  color: #a1887f;
  margin-top: 2px;
}

.divider {
  width: 1px;
  height: 36px;
  background: #e0e0e0;
}

.garment-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.garment-tag {
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.color-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 1px solid rgba(0,0,0,0.1);
  display: inline-block;
}

.inline-color {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.zone-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f5f5f5;
}
</style>
