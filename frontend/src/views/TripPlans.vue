<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon color="#ec407a"><Suitcase /></el-icon>
        出行清单
      </h2>
      <el-button type="primary" @click="openCreateDialog" size="large" v-if="!selectedPlan">
        <el-icon><Plus /></el-icon>
        新建出行计划
      </el-button>
      <div v-else class="plan-actions">
        <el-button @click="backToList">
          <el-icon><ArrowLeft /></el-icon>
          返回列表
        </el-button>
        <el-button type="warning" @click="handleRegenerate" :loading="regenerating">
          <el-icon><Refresh /></el-icon>
          重新生成推荐
        </el-button>
        <el-button type="primary" @click="openEditDialog">
          <el-icon><Edit /></el-icon>
          编辑计划
        </el-button>
        <el-popconfirm title="确认删除此出行计划？" @confirm="handleDelete">
          <template #reference>
            <el-button type="danger">
              <el-icon><Delete /></el-icon>
              删除计划
            </el-button>
          </template>
        </el-popconfirm>
      </div>
    </div>

    <div v-if="!selectedPlan">
      <el-row :gutter="20">
        <el-col :span="24" v-if="tripPlans.length === 0">
          <el-empty description="暂无出行计划，点击右上角创建">
            <el-button type="primary" @click="openCreateDialog">
              <el-icon><Plus /></el-icon>
              新建出行计划
            </el-button>
          </el-empty>
        </el-col>
        <el-col :span="8" v-for="plan in tripPlans" :key="plan.id">
          <el-card shadow="hover" class="plan-card" @click="selectPlan(plan.id)">
            <div class="plan-card-header">
              <div>
                <h3 class="plan-name">{{ plan.name }}</h3>
                <p class="plan-destination">
                  <el-icon><LocationFilled /></el-icon>
                  {{ plan.destination }}
                </p>
              </div>
              <el-tag :type="getStatusType(plan.status)" size="small" effect="dark">
                {{ plan.status }}
              </el-tag>
            </div>
            <div class="plan-card-body">
              <div class="plan-dates">
                <el-icon><Calendar /></el-icon>
                {{ plan.start_date }} 至 {{ plan.end_date }}
                <el-tag size="small" type="info">{{ plan.duration_days }}天</el-tag>
              </div>
              <div class="plan-progress">
                <div class="progress-header">
                  <span>打包进度</span>
                  <span class="progress-text">{{ plan.packed_count }}/{{ plan.items_count }}</span>
                </div>
                <el-progress 
                  :percentage="plan.items_count > 0 ? Math.round(plan.packed_count / plan.items_count * 100) : 0"
                  :stroke-width="8"
                  :color="plan.packed_count === plan.items_count ? '#67c23a' : '#409eff'"
                  show-text="false"
                />
              </div>
              <div class="plan-stats">
                <el-tag size="small" type="danger" effect="plain">必带 {{ plan.must_count }} 件</el-tag>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div v-else-if="planDetail" class="plan-detail">
      <el-card shadow="never" class="detail-header-card">
        <div class="detail-header">
          <div>
            <h3 class="plan-title">{{ planDetail.name }}</h3>
            <div class="plan-meta">
              <el-tag :type="getStatusType(planDetail.status)" size="default" effect="dark">
                {{ planDetail.status }}
              </el-tag>
              <span class="meta-item">
                <el-icon><LocationFilled /></el-icon>
                {{ planDetail.destination }}
              </span>
              <span class="meta-item">
                <el-icon><Calendar /></el-icon>
                {{ planDetail.start_date }} 至 {{ planDetail.end_date }} ({{ planDetail.duration_days }}天)
              </span>
              <span v-if="planDetail.weather_min !== null && planDetail.weather_max !== null" class="meta-item">
                <el-icon><Sunny /></el-icon>
                {{ planDetail.weather_min }}°C - {{ planDetail.weather_max }}°C
              </span>
              <span v-if="planDetail.weather_description" class="meta-item">
                {{ planDetail.weather_description }}
              </span>
              <span v-if="planDetail.activity_scenes" class="meta-item">
                <el-icon><Flag /></el-icon>
                {{ planDetail.activity_scenes }}
              </span>
              <span class="meta-item">
                <el-icon><RefreshRight /></el-icon>
                {{ planDetail.change_preference }}
              </span>
            </div>
          </div>
        </div>

        <el-row :gutter="20" class="summary-cards">
          <el-col :span="6">
            <div class="summary-card summary-must">
              <div class="summary-icon"><el-icon><StarFilled /></el-icon></div>
              <div>
                <div class="summary-value">{{ planDetail.recommendation_summary.must_carry.length }}</div>
                <div class="summary-label">必带衣物</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-card summary-optional">
              <div class="summary-icon"><el-icon><CirclePlus /></el-icon></div>
              <div>
                <div class="summary-value">{{ planDetail.recommendation_summary.optional.length }}</div>
                <div class="summary-label">备选衣物</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-card summary-wash">
              <div class="summary-icon"><el-icon><Brush /></el-icon></div>
              <div>
                <div class="summary-value">{{ planDetail.recommendation_summary.estimated_wash_after_return }}</div>
                <div class="summary-label">返程待洗护</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-card summary-wear">
              <div class="summary-icon"><el-icon><Clock /></el-icon></div>
              <div>
                <div class="summary-value">{{ planDetail.recommendation_summary.total_estimated_wears }}</div>
                <div class="summary-label">预计穿着次数</div>
              </div>
            </div>
          </el-col>
        </el-row>

        <el-alert 
          v-if="planDetail.recommendation_summary.change_gap_analysis.has_gap"
          :title="planDetail.recommendation_summary.change_gap_analysis.suggestion"
          type="warning"
          show-icon
          :closable="false"
          style="margin-top: 16px"
        >
          <template #default>
          <div class="gap-details">
            <div v-for="(gap, cat) in planDetail.recommendation_summary.change_gap_analysis.category_gaps" :key="cat" class="gap-item" v-if="gap.gap > 0">
              <span class="gap-cat">{{ cat }}</span>
              <span class="gap-info">需要 {{ gap.needed }} 件，现有 {{ gap.available }} 件，缺口 {{ gap.gap }} 件</span>
            </div>
          </div>
          </template>
        </el-alert>
      </el-card>

      <el-tabs v-model="activeTab" class="detail-tabs">
        <el-tab-pane label="推荐清单" name="recommendation">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-card shadow="never" class="recommend-card must-card">
                <template #header>
                  <div class="card-header">
                    <span class="card-title">
                      <el-icon color="#f56c6c"><StarFilled /></el-icon>
                      必带衣物
                      <el-tag type="danger" size="small">{{ planDetail.recommendation_summary.must_carry.length }}件</el-tag>
                    </span>
                  </div>
                </template>
                <div class="item-list">
                  <div
                    v-for="item in planDetail.recommendation_summary.must_carry"
                    :key="item.id"
                    class="trip-item"
                    :class="{ 'packed': item.pack_status === '已打包' }"
                  >
                    <div class="item-check">
                      <el-checkbox
                        :model-value="item.pack_status === '已打包'"
                        @change="togglePack(item.id)"
                      />
                    </div>
                    <div class="item-info">
                      <div class="item-header">
                        <span class="item-name">{{ item.garment?.name }}</span>
                        <el-tag size="small" type="danger" effect="plain">必带</el-tag>
                      </div>
                      <div class="item-meta">
                        <el-tag size="small">{{ item.garment?.category }}</el-tag>
                        <el-tag size="small" :type="getFabricTagType(item.garment?.fabric || '')" effect="plain">
                          {{ item.garment?.fabric }}
                        </el-tag>
                        <el-tag size="small" effect="plain">{{ item.garment?.color }}</el-tag>
                      </div>
                      <div class="item-reasons">
                        <el-icon><InfoFilled /></el-icon>
                        {{ item.recommend_reasons }}
                      </div>
                      <div class="item-actions">
                        <div class="quantity-control">
                          <span class="qty-label">携带数量：</span>
                          <el-input-number
                            v-model.number="item.planned_quantity"
                            :min="1"
                            :max="10"
                            size="small"
                            @change="updateItemQuantity(item)"
                          />
                        </div>
                        <el-button
                          size="small"
                          type="primary"
                          plain
                          @click="openReplaceDialog(item)"
                        >
                          <el-icon><Switch /></el-icon>
                          替换
                        </el-button>
                      </div>
                    </div>
                    <div class="item-storage" v-if="item.garment?.storage_zone">
                      <el-icon><Box /></el-icon>
                      {{ item.garment.storage_zone.name }}
                    </div>
                  </div>
                  <el-empty v-if="planDetail.recommendation_summary.must_carry.length === 0" description="暂无必带衣物" />
                </div>
              </el-card>
            </el-col>

            <el-col :span="8">
              <el-card shadow="never" class="recommend-card optional-card">
                <template #header>
                  <div class="card-header">
                    <span class="card-title">
                      <el-icon color="#e6a23c"><CirclePlus /></el-icon>
                      备选衣物
                      <el-tag type="warning" size="small">{{ planDetail.recommendation_summary.optional.length }}件</el-tag>
                    </span>
                  </div>
                </template>
                <div class="item-list">
                  <div
                    v-for="item in planDetail.recommendation_summary.optional"
                    :key="item.id"
                    class="trip-item"
                    :class="{ 'packed': item.pack_status === '已打包' }"
                  >
                    <div class="item-check">
                      <el-checkbox
                        :model-value="item.pack_status === '已打包'"
                        @change="togglePack(item.id)"
                      />
                    </div>
                    <div class="item-info">
                      <div class="item-header">
                        <span class="item-name">{{ item.garment?.name }}</span>
                        <el-tag size="small" type="warning" effect="plain">备选</el-tag>
                      </div>
                      <div class="item-meta">
                        <el-tag size="small">{{ item.garment?.category }}</el-tag>
                        <el-tag size="small" :type="getFabricTagType(item.garment?.fabric || '')" effect="plain">
                          {{ item.garment?.fabric }}
                        </el-tag>
                        <el-tag size="small" effect="plain">{{ item.garment?.color }}</el-tag>
                      </div>
                      <div class="item-reasons">
                        <el-icon><InfoFilled /></el-icon>
                        {{ item.recommend_reasons }}
                      </div>
                      <div class="item-actions">
                        <div class="quantity-control">
                          <span class="qty-label">携带数量：</span>
                          <el-input-number
                            v-model.number="item.planned_quantity"
                            :min="0"
                            :max="10"
                            size="small"
                            @change="updateItemQuantity(item)"
                          />
                        </div>
                        <el-button
                          size="small"
                          type="primary"
                          plain
                          @click="openReplaceDialog(item)"
                        >
                          <el-icon><Switch /></el-icon>
                          替换
                        </el-button>
                      </div>
                    </div>
                    <div class="item-storage" v-if="item.garment?.storage_zone">
                      <el-icon><Box /></el-icon>
                      {{ item.garment.storage_zone.name }}
                    </div>
                  </div>
                  <el-empty v-if="planDetail.recommendation_summary.optional.length === 0" description="暂无备选衣物" />
                </div>
              </el-card>
            </el-col>

            <el-col :span="8">
              <el-card shadow="never" class="recommend-card not-card">
                <template #header>
                  <div class="card-header">
                    <span class="card-title">
                      <el-icon color="#909399"><Warning /></el-icon>
                      不建议携带
                      <el-tag type="info" size="small">{{ planDetail.recommendation_summary.not_recommended.length }}件</el-tag>
                    </span>
                  </div>
                </template>
                <div class="item-list">
                  <div
                    v-for="item in planDetail.recommendation_summary.not_recommended"
                    :key="item.id"
                    class="trip-item not-recommended"
                  >
                    <div class="item-info">
                      <div class="item-header">
                        <span class="item-name">{{ item.garment?.name }}</span>
                        <el-tag size="small" type="info" effect="plain">不建议</el-tag>
                      </div>
                      <div class="item-meta">
                        <el-tag size="small">{{ item.garment?.category }}</el-tag>
                        <el-tag size="small" :type="getFabricTagType(item.garment?.fabric || '')" effect="plain">
                          {{ item.garment?.fabric }}
                        </el-tag>
                      </div>
                      <div class="item-reasons">
                        <el-icon><WarningFilled /></el-icon>
                        {{ item.recommend_reasons }}
                      </div>
                    </div>
                  </div>
                  <el-empty v-if="planDetail.recommendation_summary.not_recommended.length === 0" description="所有衣物都适合携带" />
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>

        <el-tab-pane label="按天穿搭" name="outfit">
          <el-row :gutter="20">
            <el-col :span="6" v-for="dayPlan in planDetail.day_outfit_plans" :key="dayPlan.day_index">
              <el-card shadow="never" class="day-card">
                <template #header>
                  <div class="day-header">
                    <span class="day-title">
                      <el-icon><Calendar /></el-icon>
                      第 {{ dayPlan.day_index }} 天
                    </span>
                    <el-tag size="small" type="primary">{{ dayPlan.date }}</el-tag>
                  </div>
                </template>
                <div class="day-garments">
                  <div v-for="garment in dayPlan.garments" :key="garment.id" class="day-garment">
                    <div class="garment-color" :style="{ background: getColorCode(garment.color) }"></div>
                    <div class="garment-info">
                      <div class="garment-name">{{ garment.name }}</div>
                      <div class="garment-meta">
                        <el-tag size="small">{{ garment.category }}</el-tag>
                        <el-tag size="small" effect="plain">{{ garment.fabric }}</el-tag>
                      </div>
                    </div>
                  </div>
                  <el-empty v-if="dayPlan.garments.length === 0" description="今日无安排" :image-size="60" />
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>

        <el-tab-pane label="收纳取物" name="storage">
          <el-row :gutter="20">
            <el-col :span="12" v-for="path in planDetail.storage_pickup_paths" :key="path.storage_zone_id || 'unassigned'">
              <el-card shadow="never" class="storage-card">
                <template #header>
                  <div class="storage-header">
                    <span class="storage-title">
                      <el-icon><Box /></el-icon>
                      {{ path.storage_zone_name }}
                    </span>
                    <el-tag size="small" type="info">{{ path.total_items }} 件</el-tag>
                  </div>
                </template>
                <div class="storage-items">
                  <div v-for="item in path.garments" :key="item.id" class="storage-item">
                    <div class="storage-item-check">
                      <el-checkbox :model-value="item.pack_status === '已打包'" disabled />
                    </div>
                    <div class="storage-item-info">
                      <span class="storage-item-name">{{ item.name }}</span>
                      <div class="storage-item-meta">
                        <el-tag size="small">{{ item.category }}</el-tag>
                        <el-tag size="small" effect="plain">{{ item.color }}</el-tag>
                        <el-tag size="small" :type="item.recommend_level === '必带' ? 'danger' : 'warning'" effect="plain">
                          {{ item.recommend_level }}
                        </el-tag>
                        <span class="storage-item-qty">x{{ item.quantity }}</span>
                      </div>
                    </div>
                    <el-tag size="small" :type="item.pack_status === '已打包' ? 'success' : 'info'">
                      {{ item.pack_status }}
                    </el-tag>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-dialog
      v-model="createDialogVisible"
      :title="editingPlan ? '编辑出行计划' : '新建出行计划'"
      width="640px"
      destroy-on-close
    >
      <el-form :model="planForm" label-width="120px" ref="planFormRef" :rules="planRules">
        <el-form-item label="计划名称" prop="name">
          <el-input v-model="planForm.name" placeholder="如：三亚度假、北京出差" />
        </el-form-item>
        <el-form-item label="目的地" prop="destination">
          <el-input v-model="planForm.destination" placeholder="如：海南省三亚市" />
        </el-form-item>
        <el-form-item label="出行日期" prop="dateRange">
          <el-date-picker
            v-model="planForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="最低气温">
              <el-input-number v-model="planForm.weather_min" :min="-20" :max="50" :step="1" /> °C
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最高气温">
              <el-input-number v-model="planForm.weather_max" :min="-20" :max="50" :step="1" /> °C
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="天气描述">
          <el-input v-model="planForm.weather_description" placeholder="如：晴朗、多雨、寒冷" />
        </el-form-item>
        <el-form-item label="活动场景">
          <el-select
            v-model="planForm.selectedScenes"
            multiple
            placeholder="请选择活动场景"
            style="width: 100%"
          >
            <el-option
              v-for="scene in enums?.activity_scenes"
              :key="scene.value"
              :label="scene.value"
              :value="scene.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="更换偏好" prop="change_preference">
          <el-select v-model="planForm.change_preference" style="width: 100%">
            <el-option
              v-for="pref in enums?.change_preferences"
              :key="pref.value"
              :label="pref.value"
              :value="pref.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="当前状态">
          <el-select v-model="planForm.status" style="width: 100%">
            <el-option
              v-for="status in enums?.trip_statuses"
              :key="status.value"
              :label="status.value"
              :value="status.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="planForm.notes" type="textarea" :rows="3" placeholder="其他需要注意的事项" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPlan" :loading="submitting">
          {{ editingPlan ? '保存' : '创建并生成推荐' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="replaceDialogVisible"
      title="替换衣物"
      width="720px"
      destroy-on-close
    >
      <div v-if="currentReplacingItem">
        <div class="replace-current">
          <span class="replace-label">当前衣物：</span>
          <el-tag size="small" type="danger">
            {{ currentReplacingItem.garment?.name }} ({{ currentReplacingItem.garment?.category }})
          </el-tag>
        </div>
        <el-tabs v-model="replaceCategory" class="replace-tabs">
          <el-tab-pane
            v-for="(items, cat) in planDetail?.available_replacements"
            :key="cat"
            :label="`${cat} (${items.length})`"
            :name="cat"
          >
            <div class="replace-list">
              <div
                v-for="repl in items"
                :key="repl.garment.id"
                class="replace-item"
                :class="{ 'selected': selectedReplacement?.garment.id === repl.garment.id }"
                @click="selectedReplacement = repl"
              >
                <div class="replace-item-info">
                  <div class="replace-item-header">
                    <span class="replace-item-name">{{ repl.garment.name }}</span>
                    <el-tag
                      size="small"
                      :type="repl.recommend_level === '必带' ? 'danger' : 'warning'"
                      effect="plain"
                    >
                      {{ repl.recommend_level }}
                    </el-tag>
                    <el-tag size="small" type="info" effect="plain">
                      适配度 {{ repl.score }} 分
                    </el-tag>
                  </div>
                  <div class="replace-item-meta">
                    <el-tag size="small">{{ repl.garment.fabric }}</el-tag>
                    <el-tag size="small" effect="plain">{{ repl.garment.color }}</el-tag>
                    <el-tag size="small" effect="plain">{{ repl.garment.size }}</el-tag>
                    <span v-if="repl.garment.storage_zone" class="storage-info">
                      <el-icon><Box /></el-icon>
                      {{ repl.garment.storage_zone?.name }}
                    </span>
                  </div>
                  <div class="replace-item-reasons">
                    <el-icon><InfoFilled /></el-icon>
                    {{ repl.reasons.join('；') }}
                  </div>
                </div>
              </div>
              <el-empty v-if="items.length === 0" description="该品类暂无可替换衣物" />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
      <template #footer>
        <el-button @click="replaceDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="!selectedReplacement"
          @click="confirmReplace"
          :loading="replacing"
        >
          确认替换
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, type FormInstance, type FormRules } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { tripPlanApi, tripItemApi, enumApi } from '@/api'
import type {
  TripPlanSummary, TripPlanDetail, TripItem, Enums
} from '@/types'
import {
  Suitcase, Plus, ArrowLeft, Refresh, Edit, Delete,
  LocationFilled, Calendar, Sunny, Flag, RefreshRight,
  StarFilled, CirclePlus, Brush, Clock, InfoFilled,
  Warning, WarningFilled, Box, Switch, Star
} from '@element-plus/icons-vue'

const tripPlans = ref<TripPlanSummary[]>([])
const selectedPlan = ref<number | null>(null)
const planDetail = ref<TripPlanDetail | null>(null)
const activeTab = ref('recommendation')
const enums = ref<Enums | null>(null)
const loading = ref(false)
const submitting = ref(false)
const regenerating = ref(false)
const replacing = ref(false)

const createDialogVisible = ref(false)
const replaceDialogVisible = ref(false)
const planFormRef = ref<FormInstance>()
const editingPlan = ref<TripPlanDetail | null>(null)

const planForm = reactive({
  name: '',
  destination: '',
  dateRange: [] as string[],
  weather_min: null as number | null,
  weather_max: null as number | null,
  weather_description: '',
  selectedScenes: [] as string[],
  change_preference: '每天更换',
  status: '规划中',
  notes: ''
})

const planRules: FormRules = {
  name: [{ required: true, message: '请输入计划名称', trigger: 'blur' }],
  destination: [{ required: true, message: '请输入目的地', trigger: 'blur' }],
  dateRange: [{ required: true, message: '请选择出行日期', trigger: 'change' }],
  change_preference: [{ required: true, message: '请选择更换偏好', trigger: 'change' }]
}

const currentReplacingItem = ref<TripItem | null>(null)
const selectedReplacement = ref<any>(null)
const replaceCategory = ref('')

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    '规划中': '',
    '打包中': 'warning',
    '出行中': 'primary',
    '已完成': 'success',
    '已取消': 'info'
  }
  return map[status] || ''
}

const getFabricTagType = (fabric: string) => {
  const map: Record<string, string> = {
    '纯棉': 'success', '真丝': 'warning', '蕾丝': 'danger',
    '莫代尔': 'success', '锦纶': 'info', '氨纶': 'warning',
    '聚酯纤维': 'info', '竹纤维': 'success', '羊毛': 'warning'
  }
  return map[fabric] as any || ''
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

const loadTripPlans = async () => {
  loading.value = true
  try {
    if (!enums.value) {
      enums.value = await enumApi.get()
    }
    tripPlans.value = await tripPlanApi.list()
  } catch (e) {
    ElMessage.error('加载出行计划失败')
  } finally {
    loading.value = false
  }
}

const selectPlan = async (planId: number) => {
  selectedPlan.value = planId
  await loadPlanDetail(planId)
}

const loadPlanDetail = async (planId: number) => {
  loading.value = true
  try {
    planDetail.value = await tripPlanApi.get(planId)
    const cats = Object.keys(planDetail.value.available_replacements || {})
    if (cats.length > 0) {
      replaceCategory.value = cats[0]
    }
  } catch (e) {
    ElMessage.error('加载计划详情失败')
  } finally {
    loading.value = false
  }
}

const backToList = () => {
  selectedPlan.value = null
  planDetail.value = null
  activeTab.value = 'recommendation'
}

const openCreateDialog = () => {
  editingPlan.value = null
  Object.assign(planForm, {
    name: '',
    destination: '',
    dateRange: [],
    weather_min: null,
    weather_max: null,
    weather_description: '',
    selectedScenes: [],
    change_preference: '每天更换',
    status: '规划中',
    notes: ''
  })
  createDialogVisible.value = true
}

const openEditDialog = () => {
  if (!planDetail.value) return
  editingPlan.value = planDetail.value
  Object.assign(planForm, {
    name: planDetail.value.name,
    destination: planDetail.value.destination,
    dateRange: [planDetail.value.start_date, planDetail.value.end_date],
    weather_min: planDetail.value.weather_min,
    weather_max: planDetail.value.weather_max,
    weather_description: planDetail.value.weather_description,
    selectedScenes: planDetail.value.activity_scenes ? planDetail.value.activity_scenes.split(',').map(s => s.trim()).filter(Boolean) : [],
    change_preference: planDetail.value.change_preference,
    status: planDetail.value.status,
    notes: planDetail.value.notes
  })
  createDialogVisible.value = true
}

const submitPlan = async () => {
  if (!planFormRef.value) return
  await planFormRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      const duration = planForm.dateRange.length === 2
        ? Math.ceil((new Date(planForm.dateRange[1]).getTime() - new Date(planForm.dateRange[0]).getTime()) / (1000 * 60 * 60 * 24)) + 1
        : 1

      const planData = {
        name: planForm.name,
        destination: planForm.destination,
        start_date: planForm.dateRange[0],
        end_date: planForm.dateRange[1],
        duration_days: duration,
        weather_min: planForm.weather_min,
        weather_max: planForm.weather_max,
        weather_description: planForm.weather_description,
        activity_scenes: planForm.selectedScenes.join(', '),
        change_preference: planForm.change_preference,
        status: planForm.status,
        notes: planForm.notes
      }

      if (editingPlan.value) {
        await tripPlanApi.update(editingPlan.value.id, planData)
        ElMessage.success('计划已更新')
        await loadPlanDetail(editingPlan.value.id)
      } else {
        const newPlan = await tripPlanApi.create(planData)
        ElMessage.success('计划已创建，正在生成推荐清单...')
        selectedPlan.value = newPlan.id
        await loadPlanDetail(newPlan.id)
      }
      createDialogVisible.value = false
      await loadTripPlans()
    } catch (e) {
      ElMessage.error(editingPlan.value ? '更新失败' : '创建失败')
    } finally {
      submitting.value = false
    }
  })
}

const handleRegenerate = async () => {
  if (!selectedPlan.value) return
  try {
    regenerating.value = true
    planDetail.value = await tripPlanApi.regenerate(selectedPlan.value)
    ElMessage.success('推荐已重新生成')
  } catch (e) {
    ElMessage.error('重新生成失败')
  } finally {
    regenerating.value = false
  }
}

const handleDelete = async () => {
  if (!selectedPlan.value) return
  try {
    await tripPlanApi.delete(selectedPlan.value)
    ElMessage.success('计划已删除')
    backToList()
    await loadTripPlans()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

const togglePack = async (itemId: number) => {
  try {
    await tripItemApi.togglePack(itemId)
    if (selectedPlan.value) {
      await loadPlanDetail(selectedPlan.value)
    }
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const updateItemQuantity = async (item: TripItem) => {
  try {
    await tripItemApi.update(item.id, {
      planned_quantity: item.planned_quantity
    })
    ElMessage.success('数量已更新')
  } catch (e) {
    ElMessage.error('更新失败')
  }
}

const openReplaceDialog = (item: TripItem) => {
  currentReplacingItem.value = item
  selectedReplacement.value = null
  replaceDialogVisible.value = true
}

const confirmReplace = async () => {
  if (!currentReplacingItem.value || !selectedReplacement.value) return
  try {
    replacing.value = true
    await tripItemApi.replace(
      currentReplacingItem.value.id,
      selectedReplacement.value.garment.id
    )
    ElMessage.success('替换成功')
    replaceDialogVisible.value = false
    if (selectedPlan.value) {
      await loadPlanDetail(selectedPlan.value)
    }
  } catch (e) {
    ElMessage.error('替换失败')
  } finally {
    replacing.value = false
  }
}

loadTripPlans()
</script>

<style scoped>
.plan-card {
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 20px;
}

.plan-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(236, 64, 122, 0.15);
}

.plan-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.plan-name {
  margin: 0 0 6px 0;
  font-size: 18px;
  font-weight: 600;
  color: #5d4037;
}

.plan-destination {
  margin: 0;
  color: #8d6e63;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
}

.plan-card-body {
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.plan-dates {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #8d6e63;
  font-size: 14px;
  margin-bottom: 12px;
}

.plan-progress {
  margin-bottom: 12px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 13px;
  color: #8d6e63;
}

.progress-text {
  font-weight: 600;
}

.plan-stats {
  display: flex;
  gap: 8px;
}

.detail-header-card {
  margin-bottom: 20px;
}

.plan-title {
  margin: 0 0 12px 0;
  font-size: 24px;
  font-weight: 700;
  color: #5d4037;
}

.plan-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  align-items: center;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #8d6e63;
  font-size: 14px;
}

.summary-cards {
  margin-top: 20px;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 12px;
  color: white;
}

.summary-must {
  background: linear-gradient(135deg, #f56c6c, #f78989);
}

.summary-optional {
  background: linear-gradient(135deg, #e6a23c, #f0c78a);
}

.summary-wash {
  background: linear-gradient(135deg, #67c23a, #85ce61);
}

.summary-wear {
  background: linear-gradient(135deg, #409eff, #66b1ff);
}

.summary-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.summary-value {
  font-size: 28px;
  font-weight: 700;
}

.summary-label {
  font-size: 14px;
  opacity: 0.9;
}

.gap-details {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.gap-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.gap-cat {
  font-weight: 600;
  color: #e6a23c;
}

.gap-info {
  color: #606266;
}

.detail-tabs {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #5d4037;
  font-size: 16px;
}

.recommend-card {
  height: 100%;
}

.item-list {
  max-height: 600px;
  overflow-y: auto;
  padding-right: 8px;
}

.trip-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 12px;
  background: #fafafa;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.trip-item:hover {
  border-color: #fce4ec;
}

.trip-item.packed {
  background: #f0f9eb;
  border-color: #c2e7b0;
}

.trip-item.not-recommended {
  opacity: 0.6;
}

.item-check {
  flex-shrink: 0;
  padding-top: 4px;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  gap: 8px;
}

.item-name {
  font-weight: 600;
  color: #5d4037;
  font-size: 15px;
}

.item-meta {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.item-reasons {
  font-size: 12px;
  color: #8d6e63;
  display: flex;
  align-items: flex-start;
  gap: 4px;
  margin-bottom: 10px;
  line-height: 1.5;
}

.item-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.qty-label {
  font-size: 13px;
  color: #8d6e63;
}

.item-storage {
  flex-shrink: 0;
  font-size: 12px;
  color: #8d6e63;
  display: flex;
  align-items: center;
  gap: 4px;
  padding-top: 4px;
}

.day-card {
  height: 100%;
}

.day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.day-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: #5d4037;
}

.day-garments {
  min-height: 200px;
}

.day-garment {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #fafafa;
  border-radius: 8px;
  margin-bottom: 10px;
  align-items: center;
}

.garment-color {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  flex-shrink: 0;
  border: 2px solid rgba(0,0,0,0.08);
}

.garment-info {
  flex: 1;
}

.garment-name {
  font-weight: 600;
  color: #5d4037;
  margin-bottom: 4px;
}

.garment-meta {
  display: flex;
  gap: 6px;
}

.storage-card {
  height: 100%;
}

.storage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.storage-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: #5d4037;
}

.storage-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #fafafa;
  border-radius: 8px;
  margin-bottom: 10px;
}

.storage-item-check {
  flex-shrink: 0;
}

.storage-item-info {
  flex: 1;
}

.storage-item-name {
  font-weight: 600;
  color: #5d4037;
  display: block;
  margin-bottom: 4px;
}

.storage-item-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.storage-item-qty {
  font-weight: 600;
  color: #ec407a;
  margin-left: 8px;
}

.replace-current {
  margin-bottom: 16px;
  padding: 12px;
  background: #fce4ec;
  border-radius: 8px;
}

.replace-label {
  font-weight: 600;
  color: #5d4037;
  margin-right: 8px;
}

.replace-item {
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  margin-bottom: 10px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.replace-item:hover {
  border-color: #e8a3c1;
}

.replace-item.selected {
  border-color: #ec407a;
  background: #fce4ec;
}

.replace-item-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.replace-item-name {
  font-weight: 600;
  color: #5d4037;
  font-size: 15px;
}

.replace-item-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.storage-info {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #8d6e63;
  font-size: 12px;
}

.replace-item-reasons {
  font-size: 12px;
  color: #8d6e63;
  display: flex;
  align-items: flex-start;
  gap: 4px;
  line-height: 1.5;
}

.replace-list {
  max-height: 400px;
  overflow-y: auto;
}

.plan-actions {
  display: flex;
  gap: 12px;
}

:deep(.el-tabs__content) {
  padding-top: 16px;
}

:deep(.el-card__header) {
  padding: 16px 20px;
}

:deep(.el-card__body) {
  padding: 16px 20px;
}
</style>
