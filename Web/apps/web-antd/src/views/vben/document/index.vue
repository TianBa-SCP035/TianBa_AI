<script setup lang="ts">
import { ref } from 'vue'
import buddha from './buddha.txt?raw' // 同级导入，原样文本

// 示例文档数据
const documents = ref([
  {
    id: 1,
    title: '项目介绍',
    content:
      '这是项目的介绍文档，包含项目的基本信息和使用说明。\n本项目由AI工程部——周科钢、谭奇力完成。\n一期负责人：周科钢😇--------------状态：已完工。\n二期负责人：没错还是我🤪---------状态：已完工。\n三期负责人：毫无意外不是吗🐽----状态：牛马ING。',
    date: '2025-11-13',
  },
  {
    id: 2,
    title: '开发指南',
    // 把佛祖接到正文后面，也可以只放佛祖
    content: `开发指南文档，包含开发环境搭建、代码规范等内容。\n恭喜你找到彩蛋啦(/≧▽≦)/点击关于，找到修身养性助力开发进度~\n\n${buddha}`,
    date: '2025-09-28',
    monospace: true, // 用来选择 <pre> 渲染
  },
  {
    id: 3,
    title: 'API文档',
    content: 'API接口文档，包含所有接口的详细说明和使用示例。',
    date: '2025-08-25',
  },
])

const selectedDoc = ref(documents.value[0])

function selectDoc(doc: any) {
  selectedDoc.value = doc
}
</script>

<template>
  <div class="p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-bold mb-2">项目文档</h1>
      <p class="text-gray-600">这里是项目的本地文档中心</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <!-- 左侧文档列表 -->
      <div class="md:col-span-1">
        <div class="bg-white rounded-lg shadow p-4">
          <h2 class="text-lg font-semibold mb-4">文档列表</h2>
          <div class="space-y-2">
            <div
              v-for="doc in documents"
              :key="doc.id"
              :class="[
                'p-3 rounded cursor-pointer transition-colors',
                selectedDoc.id === doc.id ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'
              ]"
              @click="selectDoc(doc)"
            >
              <div class="font-medium">{{ doc.title }}</div>
              <div class="text-sm text-gray-500">{{ doc.date }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧文档内容 -->
      <div class="md:col-span-3">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="mb-4">
            <h2 class="text-xl font-semibold">{{ selectedDoc.title }}</h2>
            <div class="text-sm text-gray-500">更新时间: {{ selectedDoc.date }}</div>
          </div>

          <!-- 等宽 ASCII 渲染：只对带 monospace 的文档生效 -->
          <div v-if="selectedDoc.monospace" class="not-prose">
            <pre
               v-text="selectedDoc.content"
               class="whitespace-pre overflow-x-auto text-[16px] leading-[1.4]
                      [font-variant-ligatures:none] [tab-size:2]"
               style="font-family: Consolas, 'Courier New', Menlo, Monaco, 'Liberation Mono', monospace;"
              />
          </div>

          <!-- 普通文档渲染：保持你原来的样式 -->
          <div v-else class="prose max-w-none">
            <div class="whitespace-pre-wrap">
              {{ selectedDoc.content }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
