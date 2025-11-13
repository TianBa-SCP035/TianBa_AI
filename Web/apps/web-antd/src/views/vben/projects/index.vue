<script setup lang="ts">
import { ref } from 'vue';

// 示例项目数据
const projects = ref([
  {
    id: 1,
    name: '多疾病项目方案生成',
    description: '多疾病项目方案生成工具',
    status: 'planning',
    progress: 1,
    lastUpdate: '2025-12-01',
  },
  {
    id: 2,
    name: 'Word项目报告生成',
    description: '企业级文档生成平台',
    status: 'active',
    progress: 90,
    lastUpdate: '2025-10-16',
  },
  {
    id: 3,
    name: 'Word项目方案生成器',
    description: '基于AI的Word文档自动生成工具',
    status: 'completed',
    progress: 100,
    lastUpdate: '2025-09-20',
  },
  {
    id: 4,
    name: '数据分析平台',
    description: '实时数据分析和可视化平台(装饰)',
    status: 'completed',
    progress: 100,
    lastUpdate: '2025-08-20',
  },
]);

const getStatusText = (status: string) => {
  const statusMap = {
    active: '进行中',
    planning: '规划中',
    completed: '已完成',
  };
  return statusMap[status as keyof typeof statusMap] || status;
};

const getStatusColor = (status: string) => {
  const colorMap = {
    active: 'text-green-600 bg-green-100',
    planning: 'text-blue-600 bg-blue-100',
    completed: 'text-gray-600 bg-gray-100',
  };
  return colorMap[status as keyof typeof colorMap] || 'text-gray-600 bg-gray-100';
};

function viewProject(project: any) {
  // 这里可以添加查看项目详情的逻辑
  console.log('查看项目:', project.name);
}

function editProject(project: any) {
  // 这里可以添加编辑项目的逻辑
  console.log('编辑项目:', project.name);
}
</script>

<template>
  <div class="p-6">
    <div class="mb-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold mb-2">本地项目</h1>
          <p class="text-gray-600">管理和查看您的所有项目</p>
        </div>
        <button class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
          新建项目
        </button>
      </div>
    </div>
    
    <!-- 项目统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-white rounded-lg shadow p-4">
        <div class="text-2xl font-bold text-blue-600">{{ projects.length }}</div>
        <div class="text-gray-600">总项目数</div>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <div class="text-2xl font-bold text-green-600">{{ projects.filter(p => p.status === 'active').length }}</div>
        <div class="text-gray-600">进行中</div>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <div class="text-2xl font-bold text-blue-600">{{ projects.filter(p => p.status === 'planning').length }}</div>
        <div class="text-gray-600">规划中</div>
      </div>
      <div class="bg-white rounded-lg shadow p-4">
        <div class="text-2xl font-bold text-gray-600">{{ projects.filter(p => p.status === 'completed').length }}</div>
        <div class="text-gray-600">已完成</div>
      </div>
    </div>
    
    <!-- 项目列表 -->
    <div class="bg-white rounded-lg shadow">
      <div class="p-4 border-b">
        <h2 class="text-lg font-semibold">项目列表</h2>
      </div>
      <div class="p-4">
        <div class="space-y-4">
          <div 
            v-for="project in projects" 
            :key="project.id"
            class="border rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div class="flex justify-between items-start mb-3">
              <div>
                <h3 class="text-lg font-semibold">{{ project.name }}</h3>
                <p class="text-gray-600 text-sm">{{ project.description }}</p>
              </div>
              <span :class="['px-2 py-1 rounded-full text-xs font-medium', getStatusColor(project.status)]">
                {{ getStatusText(project.status) }}
              </span>
            </div>
            
            <div class="mb-3">
              <div class="flex justify-between text-sm text-gray-600 mb-1">
                <span>进度</span>
                <span>{{ project.progress }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  :class="['h-2 rounded-full', project.status === 'active' ? 'bg-green-500' : 'bg-blue-500']"
                  :style="{ width: project.progress + '%' }"
                ></div>
              </div>
            </div>
            
            <div class="flex justify-between items-center">
              <div class="text-sm text-gray-500">
                最后更新: {{ project.lastUpdate }}
              </div>
              <div class="space-x-2">
                <button 
                  @click="viewProject(project)"
                  class="text-blue-600 hover:text-blue-800 text-sm"
                >
                  查看
                </button>
                <button 
                  @click="editProject(project)"
                  class="text-gray-600 hover:text-gray-800 text-sm"
                >
                  编辑
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>