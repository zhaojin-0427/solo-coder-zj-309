<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon color="#9c27b0"><DataLine /></el-icon>
        数据统计
      </h2>
      <el-button type="primary" @click="loadStats">
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
    </div>

    <el-row :gutter="20" style="margin-bottom: 24px">
      <el-col :span="6">
        <div class="kpi-card kpi-1">
          <div class="kpi-icon">
            <el-icon :size="28"><Female /></el-icon>
          </div>
          <div>
            <div class="kpi-value">{{ stats?.total_garments || 0 }}</div>
            <div class="kpi-label">衣物总数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="kpi-card kpi-2">
          <div class="kpi-icon">
            <el-icon :size="28"><Brush /></el-icon>
          </div>
          <div>
            <div class="kpi-value">{{ stats?.total_washes || 0 }}</div>
            <div class="kpi-label">累计洗护</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="kpi-card kpi-3">
          <div class="kpi-icon">
            <el-icon :size="28"><Warning /></el-icon>
          </div>
          <div>
            <div class="kpi-value">{{ deformationTotal }}</div>
            <div class="kpi-label">变形记录</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="kpi-card kpi-4">
          <div class="kpi-icon">
            <el-icon :size="28"><Timer /></el-icon>
          </div>
          <div>
            <div class="kpi-value">{{ avgWashPerGarment }}</div>
            <div class="kpi-label">平均洗护/件</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="never" class="stats-card chart-card">
          <h3 class="chart-title">
            <el-icon><PieChart /></el-icon>
            面料分布统计
          </h3>
          <div ref="fabricChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" class="stats-card chart-card">
          <h3 class="chart-title">
            <el-icon><Histogram /></el-icon>
            各面料平均使用周期
          </h3>
          <div ref="fabricUseChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card shadow="never" class="stats-card chart-card">
          <h3 class="chart-title">
            <el-icon><TrendCharts /></el-icon>
            月度洗护趋势
          </h3>
          <div ref="washTrendChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" class="stats-card chart-card">
          <h3 class="chart-title">
            <el-icon><Warning /></el-icon>
            变形高发品类 TOP
          </h3>
          <div ref="deformationChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card shadow="never" class="stats-card">
          <h3 class="chart-title">
            <el-icon><Clock /></el-icon>
            长期闲置衣物（60天以上未使用）
            <el-tag size="small" type="danger" style="margin-left: 8px">
              {{ stats?.idle_garments?.length || 0 }} 件
            </el-tag>
          </h3>
          <el-table
            :data="stats?.idle_garments || []"
            size="small"
            v-if="stats?.idle_garments?.length"
          >
            <el-table-column prop="name" label="衣物名称" />
            <el-table-column prop="category" label="品类" width="100" />
            <el-table-column label="闲置天数" width="120">
              <template #default="{ row }">
                <el-tag type="danger" effect="light">{{ row.idle_days }} 天</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="use_count" label="使用次数" width="100" align="center" />
            <el-table-column label="上次穿着" width="120">
              <template #default="{ row }">
                {{ row.last_worn_date || '从未' }}
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-else description="暂无闲置衣物，做得好！" />
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="never" class="stats-card">
          <h3 class="chart-title">
            <el-icon><Coin /></el-icon>
            洗护频次 TOP（每洗之间使用次数）
          </h3>
          <el-table
            :data="stats?.wash_frequency_stats || []"
            size="small"
            v-if="stats?.wash_frequency_stats?.length"
          >
            <el-table-column type="index" label="排名" width="60" align="center" />
            <el-table-column prop="name" label="衣物名称" />
            <el-table-column prop="category" label="品类" width="100" />
            <el-table-column label="使用/每次洗护" width="130">
              <template #default="{ row }">
                <el-tag
                  :type="row.uses_per_wash > 5 ? 'danger' : row.uses_per_wash > 3 ? 'warning' : 'success'"
                  effect="light"
                >
                  {{ row.uses_per_wash }} 次/洗
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="总使用/洗护">
              <template #default="{ row }">
                {{ row.use_count }} / {{ row.wash_count }}
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-else description="洗护记录不足（至少使用5次以上才统计）" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card shadow="never" class="stats-card">
          <h3 class="chart-title">
            <el-icon><Grid /></el-icon>
            品类与面料详细统计
          </h3>
          <el-row :gutter="20">
            <el-col :span="12">
              <h4 class="sub-title">面料维度</h4>
              <el-table :data="stats?.fabric_stats || []" size="small" border>
                <el-table-column prop="fabric" label="面料" width="100" />
                <el-table-column prop="count" label="件数" width="80" align="center" />
                <el-table-column label="平均使用周期">
                  <template #default="{ row }">
                    {{ row.avg_use_cycle }} 次
                  </template>
                </el-table-column>
                <el-table-column label="平均洗护次数">
                  <template #default="{ row }">
                    {{ row.avg_wash_count }} 次
                  </template>
                </el-table-column>
                <el-table-column label="平均拥有时长">
                  <template #default="{ row }">
                    {{ row.avg_months_owned }} 个月
                  </template>
                </el-table-column>
              </el-table>
            </el-col>
            <el-col :span="12">
              <h4 class="sub-title">品类维度</h4>
              <el-table :data="stats?.category_stats || []" size="small" border>
                <el-table-column prop="category" label="品类" width="100" />
                <el-table-column prop="count" label="件数" width="80" align="center" />
                <el-table-column label="平均使用次数">
                  <template #default="{ row }">
                    {{ row.avg_uses }} 次
                  </template>
                </el-table-column>
                <el-table-column label="平均洗护次数">
                  <template #default="{ row }">
                    {{ row.avg_washes }} 次
                  </template>
                </el-table-column>
              </el-table>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { statisticsApi } from '@/api'
import type { Statistics } from '@/types'
import * as echarts from 'echarts'
import {
  DataLine, Refresh, Female, Brush, Warning, Timer,
  PieChart, Histogram, TrendCharts, Clock, Coin, Grid
} from '@element-plus/icons-vue'

const stats = ref<Statistics | null>(null)
const fabricChartRef = ref<HTMLElement | null>(null)
const fabricUseChartRef = ref<HTMLElement | null>(null)
const washTrendChartRef = ref<HTMLElement | null>(null)
const deformationChartRef = ref<HTMLElement | null>(null)

let fabricChart: echarts.ECharts | null = null
let fabricUseChart: echarts.ECharts | null = null
let washTrendChart: echarts.ECharts | null = null
let deformationChart: echarts.ECharts | null = null

const deformationTotal = computed(() => {
  if (!stats.value) return 0
  return stats.value.deformation_risk_categories.reduce((sum, cat) => sum + cat.deformation_count, 0)
})

const avgWashPerGarment = computed(() => {
  if (!stats.value || !stats.value.total_garments) return 0
  return (stats.value.total_washes / stats.value.total_garments).toFixed(1)
})

const loadStats = async () => {
  try {
    stats.value = await statisticsApi.get()
    await nextTick()
    renderCharts()
  } catch (e) {
    ElMessage.error('加载统计数据失败')
  }
}

const getFabricColors = () => [
  '#ec407a', '#ab47bc', '#7e57c2', '#5c6bc0',
  '#42a5f5', '#26c6da', '#66bb6a', '#ffa726',
  '#ef5350', '#8d6e63', '#bdbdbd'
]

const renderCharts = () => {
  if (fabricChartRef.value && stats.value) {
    if (fabricChart) fabricChart.dispose()
    fabricChart = echarts.init(fabricChartRef.value)
    fabricChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c}件 ({d}%)' },
      legend: { bottom: 0, type: 'scroll' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
        label: { show: true, formatter: '{b}\n{c}件' },
        data: stats.value.fabric_stats.map((s, i) => ({
          value: s.count,
          name: s.fabric,
          itemStyle: { color: getFabricColors()[i % getFabricColors().length] }
        }))
      }]
    })
  }

  if (fabricUseChartRef.value && stats.value) {
    if (fabricUseChart) fabricUseChart.dispose()
    fabricUseChart = echarts.init(fabricUseChartRef.value)
    fabricUseChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['平均使用次数', '平均洗护次数'] },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: stats.value.fabric_stats.map(s => s.fabric),
        axisLabel: { rotate: 30 }
      },
      yAxis: { type: 'value' },
      series: [
        {
          name: '平均使用次数',
          type: 'bar',
          data: stats.value.fabric_stats.map(s => s.avg_use_cycle),
          itemStyle: { color: '#7e57c2' },
          barWidth: '35%'
        },
        {
          name: '平均洗护次数',
          type: 'bar',
          data: stats.value.fabric_stats.map(s => s.avg_wash_count),
          itemStyle: { color: '#26c6da' },
          barWidth: '35%'
        }
      ]
    })
  }

  if (washTrendChartRef.value && stats.value) {
    if (washTrendChart) washTrendChart.dispose()
    washTrendChart = echarts.init(washTrendChartRef.value)
    washTrendChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['总洗护次数', '洗护后变形'] },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: stats.value.monthly_wash_trend.map(t => t.month)
      },
      yAxis: { type: 'value' },
      series: [
        {
          name: '总洗护次数',
          type: 'line',
          smooth: true,
          data: stats.value.monthly_wash_trend.map(t => t.total_washes),
          areaStyle: { color: 'rgba(126, 87, 194, 0.2)' },
          lineStyle: { color: '#7e57c2', width: 3 },
          itemStyle: { color: '#7e57c2' }
        },
        {
          name: '洗护后变形',
          type: 'line',
          smooth: true,
          data: stats.value.monthly_wash_trend.map(t => t.washes_with_deformation),
          lineStyle: { color: '#ef5350', width: 2, type: 'dashed' },
          itemStyle: { color: '#ef5350' }
        }
      ]
    })
  }

  if (deformationChartRef.value && stats.value) {
    if (deformationChart) deformationChart.dispose()
    deformationChart = echarts.init(deformationChartRef.value)
    const sorted = [...stats.value.deformation_risk_categories]
      .sort((a, b) => b.deformation_rate - a.deformation_rate)
      .filter(c => c.deformation_count > 0)
    deformationChart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: (params: any[]) => {
          const p = params[0]
          const item = sorted[p.dataIndex]
          return `${p.name}<br/>变形: ${item.deformation_count}/${item.total_count}件<br/>变形率: ${p.value}%`
        }
      },
      grid: { left: '3%', right: '10%', bottom: '3%', containLabel: true },
      xAxis: { type: 'value', max: 100 },
      yAxis: {
        type: 'category',
        data: sorted.map(s => s.category).reverse()
      },
      series: [{
        type: 'bar',
        data: sorted.map(s => ({
          value: s.deformation_rate,
          itemStyle: {
            color: s.deformation_rate >= 30 ? '#ef5350' : s.deformation_rate >= 15 ? '#ffa726' : '#66bb6a'
          }
        })).reverse(),
        label: {
          show: true,
          position: 'right',
          formatter: '{c}%',
          fontWeight: 'bold'
        },
        barWidth: '60%'
      }]
    })
  }
}

const handleResize = () => {
  fabricChart?.resize()
  fabricUseChart?.resize()
  washTrendChart?.resize()
  deformationChart?.resize()
}

onMounted(async () => {
  await loadStats()
  window.addEventListener('resize', handleResize)
})
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

.kpi-1 { background: linear-gradient(135deg, #ec407a, #f06292); }
.kpi-2 { background: linear-gradient(135deg, #7e57c2, #9575cd); }
.kpi-3 { background: linear-gradient(135deg, #ef5350, #e57373); }
.kpi-4 { background: linear-gradient(135deg, #26c6da, #4dd0e1); }

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

.chart-card {
  padding-bottom: 0;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #5d4037;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-box {
  height: 320px;
  width: 100%;
}

.sub-title {
  font-size: 14px;
  font-weight: 600;
  color: #8d6e63;
  margin: 0 0 12px 0;
}
</style>
