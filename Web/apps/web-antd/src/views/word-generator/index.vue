<script lang="ts" setup>
import { ref } from 'vue';
import { message } from 'ant-design-vue';
import {
  DownloadOutlined,
  FileTextOutlined,
  LoadingOutlined,
  CloudUploadOutlined,
} from '@ant-design/icons-vue';

const projectCode = ref('');
const loading = ref(false);
const downloadUrl = ref('');
const error = ref('');
const progressPercent = ref(0);
const showResult = ref(false);
const isGenerating = ref(false);

// 新增：疾病类型和语言选择
const selectedDisease = ref('tumor');
const selectedLanguage = ref('chinese');

// 疾病类型选项
const diseaseOptions = ref([
  { value: 'tumor', label: '肿瘤' },
  { value: 'autoimmune', label: '自身免疫' },
]);

// 模糊匹配函数
const filterOption = (input: string, option: any) => {
  const label = option.label.toLowerCase();
  const value = input.toLowerCase();
  
  // 检查输入的每个字符是否都存在于标签中
  return [...value].every(char => label.includes(char));
};

const generateProjectPlan = async () => {
  if (!projectCode.value.trim()) {
    message.error('请输入项目编号');
    return;
  }
  loading.value = true;
  isGenerating.value = true;
  error.value = '';
  downloadUrl.value = '';
  showResult.value = false;
  progressPercent.value = 0;

  const progressInterval = setInterval(() => {
    if (progressPercent.value < 90) {
      progressPercent.value += Math.random() * 16;
      if (progressPercent.value > 90) progressPercent.value = 90;
    }
  }, 300);

  try {
    const resp = await fetch(
      `${import.meta.env.VITE_GLOB_API_URL_PLAN}/project-plan/execute`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          disease: selectedDisease.value, 
          language: selectedLanguage.value, 
          content: { project_code: projectCode.value.trim() } 
        }),
      }
    );

    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

    const blob = await resp.blob();
    downloadUrl.value = URL.createObjectURL(blob);
    progressPercent.value = 100;
    message.success('项目方案生成成功！');
    showResult.value = true;
  } catch (e) {
    console.error(e);
    error.value = '生成项目方案失败，请检查项目编号或网络连接';
    message.error('生成项目方案失败');
  } finally {
    clearInterval(progressInterval);
    loading.value = false;
    isGenerating.value = false;
  }
}; // ←←← 这行是你缺少的

const downloadFile = () => {
  if (!downloadUrl.value) return;
  const a = document.createElement('a');
  a.href = downloadUrl.value;
  // 根据语言选择决定文件名
  const fileSuffix = selectedLanguage.value === 'chinese' ? '项目方案.docx' : 'Study Protocol.docx';
  a.download = `${projectCode.value}_${fileSuffix}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(downloadUrl.value);
  downloadUrl.value = '';
  showResult.value = false;
  progressPercent.value = 0;
};

const resetForm = () => {
  projectCode.value = '';
  error.value = '';
  downloadUrl.value = '';
  showResult.value = false;
  progressPercent.value = 0;
};
</script>

<template>
  <div
    data-title="word项目方案生成器"
    data-description="智能word项目方案生成器，一键生成专业项目文档"
  >
    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 标题区域 -->
      <div class="header-section">
        <div class="title-container">
          <FileTextOutlined class="title-icon" />
          <h1 class="main-title">智能项目方案生成器</h1>
          <p class="subtitle">基于ai技术的专业word文档自动生成工具</p>
        </div>
      </div>

      <!-- 主要功能卡片 -->
      <a-card class="main-card" :bordered="false">
        <template #title>
          <CloudUploadOutlined class="card-title-icon" />
          <span>生成项目方案</span>
        </template>

        <!-- 输入区域 -->
        <div class="input-section">
          <a-alert
            message="使用说明"
            description="请输入有效的项目编号（如：25P1156），系统将自动查询数据库并生成专业的项目方案文档。"
            type="info"
            show-icon
            class="usage-alert"
          />

          <div class="input-group">
            <label for="projectcode" class="input-label">
              <FileTextOutlined class="label-icon" />
              项目编号
            </label>
            <a-input
              id="projectcode"
              v-model:value="projectCode"
              placeholder="请输入项目编号（例如：25P1156）"
              size="large"
              :disabled="loading"
              class="project-input"
              allow-clear
            />
          </div>

          <!-- 疾病类型和语言选择 -->
          <div class="selection-group">
            <div class="disease-selector">
              <label class="selection-label">疾病类型</label>
              <a-select
                v-model:value="selectedDisease"
                placeholder="选择疾病类型"
                size="large"
                :disabled="loading"
                show-search
                :filter-option="filterOption"
                class="disease-select"
              >
                <a-select-option
                  v-for="option in diseaseOptions"
                  :key="option.value"
                  :value="option.value"
                  :label="option.label"
                >
                  {{ option.label }}
                </a-select-option>
              </a-select>
            </div>
            
            <div class="language-toggle">
              <label class="selection-label">语言</label>
              <div class="toggle-container">
                <span :class="['lang-option', { active: selectedLanguage === 'chinese' }]">中文</span>
                <a-switch
                  v-model:checked="selectedLanguage"
                  :checked-value="'english'"
                  :un-checked-value="'chinese'"
                  class="language-switch"
                />
                <span :class="['lang-option', { active: selectedLanguage === 'english' }]">English</span>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <a-button
              type="primary"
              size="large"
              :loading="loading"
              :disabled="!projectCode.trim()"
              @click="generateProjectPlan"
              class="generate-btn"
            >
              <template #icon>
                <CloudUploadOutlined v-if="!loading" />
                <LoadingOutlined v-else />
              </template>
              {{ loading ? '生成中...' : '生成项目方案' }}
            </a-button>

            <a-button
              size="large"
              @click="resetForm"
              :disabled="loading"
              class="reset-btn"
            >
              重置
            </a-button>
          </div>

          <!-- 进度条 -->
          <div v-if="isGenerating" class="progress-section">
            <a-progress
              :percent="Math.round(progressPercent)"
              :show-info="true"
              :stroke-color="{ '0%': '#108ee9', '100%': '#87d068' }"
              stroke-linecap="square"
            />
            <p class="progress-text">正在生成项目方案，请稍候...</p>
          </div>

          <!-- 错误信息 -->
          <div v-if="error" class="error-section">
            <a-alert :message="error" type="error" show-icon />
          </div>

          <!-- 成功结果 -->
          <div v-if="showResult" class="result-section">
            <a-result
              status="success"
              title="项目方案生成成功！"
              sub-title="您的项目方案文档已准备就绪，点击下方按钮即可下载。"
            >
              <template #extra>
                <a-button
                  type="primary"
                  size="large"
                  @click="downloadFile"
                  class="download-btn"
                >
                  <template #icon><DownloadOutlined /></template>
                  下载项目方案文档
                </a-button>
                <a-button
                  size="large"
                  @click="resetForm"
                  class="new-doc-btn"
                >
                  生成新文档
                </a-button>
              </template>
            </a-result>
          </div>
        </div>
      </a-card>

      <!-- 功能特性说明 -->
      <div class="features-section">
        <a-card class="feature-card" :bordered="false">
          <template #title>
            <span>功能特性</span>
          </template>
          <div class="features-grid">
            <div class="feature-item">
              <div class="feature-icon">🚀</div>
              <h4>快速生成</h4>
              <p>一键生成专业项目方案文档，节省大量时间</p>
            </div>
            <div class="feature-item">
              <div class="feature-icon">📊</div>
              <h4>数据驱动</h4>
              <p>基于真实数据库信息，确保文档准确性</p>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🎨</div>
              <h4>专业模板</h4>
              <p>使用标准化模板，文档格式规范美观</p>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🔒</div>
              <h4>安全可靠</h4>
              <p>本地化处理，数据安全有保障</p>
            </div>
          </div>
        </a-card>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 主要内容布局 */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 10px 20px;
  position: relative;
  z-index: 1;
}
/* 标题区域 */
.header-section {
  text-align: center;
  margin-bottom: 5px;
}

.title-container {
  display: inline-block;
  background: #ffffff;
  padding: 22px 38px;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  margin-bottom: 5px;
}

.title-icon {
  font-size: 44px;
  color: #667eea;
  margin-bottom: 8px;
}

.main-title {
  font-size: 30px;
  font-weight: bold;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 15px;
  color: #7f8c8d;
  margin: 0;
}

/* 主要卡片 */
.main-card {
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.card-title-icon {
  margin-right: 8px;
  color: #667eea;
}

/* 输入区域 */
.input-section {
  padding: 2px 20px 20px;
}

.usage-alert {
  margin-bottom: 20px;
  padding: 10px 16px;
}

.input-group {
  margin-bottom: 25px;
}

.input-label {
  display: flex;
  align-items: center;
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 8px;
}

.label-icon {
  margin-right: 8px;
  color: #667eea;
}

.project-input {
  width: 100%;
  border-radius: 10px;
}

/* 疾病类型和语言选择 */
.selection-group {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.disease-selector,
.language-toggle {
  flex: 1;
}

.selection-label {
  display: block;
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 8px;
}

.disease-select {
  width: 100%;
  border-radius: 10px;
}

.toggle-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.lang-option {
  font-weight: 500;
  color: #7f8c8d;
  transition: color 0.3s ease;
}

.lang-option.active {
  color: #667eea;
}

.language-switch {
  min-width: 50px;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.generate-btn {
  flex: 1;
  height: 50px;
  border-radius: 10px;
  font-weight: 500;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
}

.generate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.reset-btn {
  min-width: 120px;
  height: 50px;
  border-radius: 10px;
  font-weight: 500;
}

/* 进度条 */
.progress-section {
  margin: 20px 0;
}

.progress-text {
  text-align: center;
  color: #667eea;
  margin-top: 10px;
  font-weight: 500;
}

/* 错误和结果区域 */
.error-section,
.result-section {
  margin-top: 20px;
}

.download-btn {
  height: 50px;
  border-radius: 10px;
  font-weight: 500;
  background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
  border: none;
  box-shadow: 0 4px 15px rgba(86, 171, 47, 0.4);
  margin-right: 15px;
}

.new-doc-btn {
  height: 50px;
  border-radius: 10px;
  font-weight: 500;
}

/* 功能特性 */
.features-section {
  margin-top: 20px;
}

.feature-card {
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  padding: 15px;
}

.feature-item {
  text-align: center;
  padding: 15px;
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.8);
  transition: transform 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-5px);
}

.feature-icon {
  font-size: 40px;
  margin-bottom: 10px;
}

.feature-item h4 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.feature-item p {
  color: #7f8c8d;
  font-size: 14px;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    padding: 10px;
  }
  .title-container {
    padding: 20px 30px;
  }
  .main-title {
    font-size: 24px;
  }
  .action-buttons {
    flex-direction: column;
  }
  .features-grid {
    grid-template-columns: 1fr;
  }
  .selection-group {
    flex-direction: column;
    gap: 15px;
  }
}
</style>
