<template>
  <div class="report-generator-container">
    <!-- 装饰性背景元素 -->
    <div class="decorative-background">
      <div v-for="(shape, i) in shapes" :key="`shape-${i}`" class="floating-shape" :style="generateStyle(shape)" />
      <div class="floating-particles">
        <div v-for="(particle, index) in 20" :key="index" class="particle" :style="getParticleStyle(index)"></div>
      </div>
      <!-- 新增动态装饰元素 -->
      <div v-for="(orb, i) in orbs" :key="`orb-${i}`" class="floating-orb" :style="generateStyle(orb)" />
      <div v-for="(geo, i) in geometries" :key="`geo-${i}`" class="geometric-shape" :style="generateStyle(geo)" />
      <div v-for="(beam, i) in beams" :key="`beam-${i}`" class="light-beam" :style="generateStyle(beam)" />
    </div>
    
    <!-- 添加全屏彩带特效 -->
    <div v-if="showConfetti" class="confetti-container" :class="{ 'show-animation': showConfetti }">
      <!-- 左下角彩带 -->
      <div v-for="(confetti, index) in 60" :key="'left-'+index" class="confetti-left" :style="getConfettiLeftStyle(index)"></div>
      <!-- 右下角彩带 -->
      <div v-for="(confetti, index) in 60" :key="'right-'+index" class="confetti-right" :style="getConfettiRightStyle(index)"></div>
    </div>
    
    <div class="report-header">
      <div class="header-icon">
        <div class="icon-text">📊</div>
        <div class="icon-decoration"></div>
      </div>
      <h1 class="report-title">报告生成器</h1>
      <p class="report-description">输入实验编号，一键生成专业分析报告</p>
    </div>

    <div class="report-content">
      <div class="input-section">
        <div class="form-row">
          <div class="form-group project-number-group">
            <label for="projectNumber" class="form-label">
              <span class="label-icon">🔍</span>
              实验编号
            </label>
            <div class="input-wrapper">
              <input
                id="projectNumber"
                v-model="projectNumber"
                type="text"
                class="form-input"
                placeholder="请输入实验编号 (如: 25P082901)"
                @keyup.enter="generateReport"
              />
              <div class="input-decoration"></div>
              <div class="input-glow"></div>
            </div>
          </div>
          
          <div class="form-group end-day-group">
            <label for="endDay" class="form-label">
              <span class="label-icon">📅</span>
              结束天
            </label>
            <div class="input-wrapper">
              <input
                id="endDay"
                v-model="endDay"
                type="text"
                class="form-input"
                placeholder="可选"
                @keyup.enter="generateReport"
                @input="validateEndDay"
              />
              <div class="input-decoration"></div>
              <div class="input-glow"></div>
            </div>
          </div>
        </div>
        
        <!-- 疾病类型和语言选择 -->
        <div class="form-row">
          <div class="form-group disease-type-group">
            <label class="form-label">
              疾病类型
            </label>
            <a-select
              v-model:value="selectedDisease"
              placeholder="请选择疾病类型"
              class="disease-select"
              :disabled="isGenerating"
              :options="diseaseOptions"
              :filter-option="filterOption"
              show-search
            />
          </div>
          
          <div class="form-group language-group">
            <label class="form-label">
              语言
            </label>
            <div class="language-switch">
              <span :class="{ active: !isEnglish }">中文</span>
              <a-switch
                v-model:checked="isEnglish"
                :disabled="isGenerating"
              />
              <span :class="{ active: isEnglish }">English</span>
            </div>
          </div>
        </div>
        
        <div class="button-container">
          <button
            :disabled="isGenerating || !projectNumber.trim()"
            class="generate-button"
            @click="generateReport"
          >
            <span v-if="!isGenerating" class="button-content">
              <span class="button-icon">✨</span>
              <span>生成报告</span>
            </span>
            <span v-else class="button-content">
              <span class="loading-spinner"></span>
              <span>生成中...</span>
            </span>
            <div class="button-shine"></div>
          </button>
        </div>
      </div>

      <!-- 默认显示的进度条区域 -->
      <div class="progress-section" :class="{ 'active': isGenerating }">
        <div class="progress-header">
          <div class="progress-icon">⚙️</div>
          <h3 class="progress-title">{{ isGenerating ? '正在生成报告' : '准备生成报告' }}</h3>
        </div>
        <div class="progress-bar-container">
          <div class="progress-bar" :style="{ width: `${progress}%` }"></div>
          <div class="progress-glow" :style="{ width: `${progress}%` }"></div>
          <div class="progress-particles">
            <div v-for="(particle, index) in 8" :key="index" class="progress-particle" :style="getProgressParticleStyle(index)"></div>
          </div>
        </div>
        <p class="progress-text">{{ isGenerating ? getProgressMessage() + ' ' + progress + '%' : '等待输入实验编号...' }}</p>
        <div class="progress-steps">
          <div 
            v-for="(step, index) in progressSteps" 
            :key="index" 
            class="step-item"
            :class="{ 'active': isGenerating && progress > index * (100 / progressSteps.length) }"
          >
            <div class="step-icon">{{ step.icon }}</div>
            <div class="step-text">{{ step.text }}</div>
            <div class="step-indicator"></div>
          </div>
        </div>
      </div>

      <div v-if="error" class="error-section">
        <div class="error-icon">⚠️</div>
        <h3 class="error-title">生成失败</h3>
        <p class="error-message">{{ error }}</p>
        <div class="error-actions">
          <button class="retry-button" @click="retryWithCorrection">
            <span class="button-icon">🔄</span>
            <span>重试</span>
          </button>
        </div>
      </div>

      <div v-if="reportGenerated" class="result-section" ref="resultSectionRef">
        <!-- 添加动态背景元素 -->
        <div v-for="(ball, i) in balls" :key="`ball-${i}`" class="floating-ball" :style="generateStyle(ball)" />
        <!-- 添加上浮小球效果 -->
        <div class="success-floating-particles">
          <div v-for="(particle, index) in 30" :key="index" class="success-particle-bg" :style="getSuccessParticleBgStyle(index)"></div>
        </div>
        
        <div class="result-header">
          <div class="success-animation">
            <div class="success-icon-container">
              <div class="success-icon">🎉</div>
              <div class="success-icon-bg"></div>
            </div>
            <div class="success-particles">
              <div v-for="(particle, index) in 20" :key="index" class="success-particle" :style="getSuccessParticleStyle(index)"></div>
            </div>
            <div class="success-sparkles">
              <div v-for="(sparkle, index) in 16" :key="index" class="success-sparkle" :style="getSuccessSparkleStyle(index)"></div>
            </div>
          </div>
          <h2 class="result-title">报告生成成功</h2>
          <p class="result-description">项目 {{ projectNumber }} 的分析报告已生成</p>
        </div>
        
        <div class="result-details">
          <div class="details-row">
            <div class="detail-item">
              <div class="detail-icon">📄</div>
              <div class="detail-text">
                <div class="detail-label">Word文档</div>
                <div class="detail-value">{{ reportData?.files.word_document.name || '项目报告.docx' }}</div>
                <div class="detail-status" :class="{ 'status-exists': reportData?.files.word_document.exists, 'status-missing': !reportData?.files.word_document.exists }">
                  {{ reportData?.files.word_document.exists ? '✅ 已生成' : '❌ 不存在' }}
                </div>
              </div>
            </div>
            <div class="detail-item">
              <div class="detail-icon">📊</div>
              <div class="detail-text">
                <div class="detail-label">终版Excel</div>
                <div class="detail-value">{{ reportData?.files.final_excel.name || '项目_Final.xlsx' }}</div>
                <div class="detail-status" :class="{ 'status-exists': reportData?.files.final_excel.exists, 'status-missing': !reportData?.files.final_excel.exists }">
                  {{ reportData?.files.final_excel.exists ? '✅ 已生成' : '❌ 不存在' }}
                </div>
              </div>
            </div>
          </div>
          <div class="details-row">
            <div class="detail-item">
              <div class="detail-icon">📋</div>
              <div class="detail-text">
                <div class="detail-label">明细Excel</div>
                <div class="detail-value">{{ reportData?.files.details_excel.name || '项目_明细.xlsx' }}</div>
                <div class="detail-status" :class="{ 'status-exists': reportData?.files.details_excel.exists, 'status-missing': !reportData?.files.details_excel.exists }">
                  {{ reportData?.files.details_excel.exists ? '✅ 已生成' : '❌ 不存在' }}
                </div>
              </div>
            </div>
            <div class="detail-item">
              <div class="detail-icon">🖼️</div>
              <div class="detail-text">
                <div class="detail-label">图片压缩包</div>
                <div class="detail-value">{{ reportData?.files.images_zip?.name || '项目图片.zip' }}</div>
                <div class="detail-status" :class="{ 'status-exists': reportData?.files.images_zip?.exists, 'status-missing': !reportData?.files.images_zip?.exists }">
                  {{ reportData?.files.images_zip?.exists ? '✅ 已生成' : '❌ 不存在' }}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="result-actions">
          <button class="action-button" @click="downloadWordDocument" :disabled="!reportData?.files.word_document.exists">
            <span class="button-icon">⬇️</span>
            <span>下载Word文档</span>
            <div class="button-shine"></div>
          </button>
          <button class="action-button secondary" @click="downloadFile('final')" :disabled="!reportData?.files.final_excel.exists">
            <span class="button-icon">📊</span>
            <span>下载终版Excel</span>
          </button>
          <button class="action-button secondary" @click="downloadFile('details')" :disabled="!reportData?.files.details_excel.exists">
            <span class="button-icon">📋</span>
            <span>下载明细Excel</span>
          </button>
          <button class="action-button secondary" @click="downloadImagesZip" :disabled="!reportData?.files.images_zip?.exists">
            <span class="button-icon">🖼️</span>
            <span>下载图片压缩包</span>
          </button>
          <button class="action-button secondary" @click="resetForm">
            <span class="button-icon">🔄</span>
            <span>生成新报告</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onBeforeUnmount, watch, onMounted, nextTick, computed } from 'vue';
import { useRoute } from 'vue-router';
import { Select as ASelect, Switch as ASwitch } from 'ant-design-vue';

// 计时器变量，用于在组件卸载时清理
let progressInterval: number | null = null;
let completeInterval: number | null = null;

const projectNumber = ref('');
const endDay = ref('');
const isGenerating = ref(false);
const progress = ref(0);
const reportGenerated = ref(false);
const error = ref('');
const reportBlobUrl = ref('');
const showConfetti = ref(false);

// 新增：疾病类型和语言选择
const selectedDisease = ref('tumor');
const selectedLanguage = ref('chinese');

// 语言切换相关
const isEnglish = computed({
  get: () => selectedLanguage.value === 'english',
  set: (value) => selectedLanguage.value = value ? 'english' : 'chinese'
});

// 疾病类型选项
const diseaseOptions = [
  { value: 'tumor', label: '肿瘤' },
  { value: 'autoimmune', label: '自身免疫' }
];

// 模糊匹配函数
const filterOption = (input: string, option: any) => {
  const label = option.label.toLowerCase();
  const value = input.toLowerCase();
  
  // 检查输入的每个字符是否都存在于标签中
  return [...value].every(char => label.includes(char));
};

// 添加新的响应式变量存储文件信息
const reportData = ref<ReportResponse | null>(null);

// 结果区域的ref，用于自动滚动
const resultSectionRef = ref<HTMLElement | null>(null);

const progressSteps = [
  { icon: '🔍', text: '查询项目信息' },
  { icon: '📊', text: '分析项目数据' },
  { icon: '📈', text: '生成统计图表' },
  { icon: '📝', text: '编写报告内容' },
  { icon: '✅', text: '完成报告生成' }
];

const getProgressMessage = () => {
  const stepIndex = Math.min(Math.floor(progress.value / 20), progressSteps.length - 1);
  return progressSteps[stepIndex].text + '...';
};

// 装饰元素数据
const shapes = [
  { width: '80px', height: '80px', top: '10%', left: '5%', right: '', bottom: '', 'delay-float': '0s', 'delay-rotate': '0s' },
  { width: '120px', height: '120px', top: '60%', left: '', right: '5%', bottom: '', 'delay-float': '0.5s', 'delay-rotate': '1s' },
  { width: '60px', height: '60px', top: '', left: '15%', right: '', bottom: '15%', 'delay-float': '1s', 'delay-rotate': '1.5s' },
  { width: '100px', height: '100px', top: '15%', left: '', right: '15%', bottom: '', 'delay-float': '0.3s', 'delay-rotate': '1.8s' },
  { width: '70px', height: '70px', top: '40%', left: '8%', right: '', bottom: '', 'delay-float': '0.7s', 'delay-rotate': '1.2s' }
];

const orbs = [
  { width: '100px', height: '100px', top: '15%', left: '10%', right: '', bottom: '', delay: '0s' },
  { width: '70px', height: '70px', top: '60%', left: '', right: '15%', bottom: '', delay: '0.8s' },
  { width: '50px', height: '50px', top: '', left: '20%', right: '', bottom: '20%', delay: '1.6s' }
];

const geometries = [
  { width: '60px', height: '60px', top: '25%', left: '', right: '25%', bottom: '', delay: '0s', 'clip-path': 'polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)' },
  { width: '80px', height: '80px', top: '', left: '', right: '10%', bottom: '30%', delay: '0.7s', 'clip-path': 'polygon(50% 0%, 100% 38%, 82% 100%, 18% 100%, 0% 38%)' },
  { width: '40px', height: '40px', top: '50%', left: '5%', right: '', bottom: '', delay: '1.5s', 'clip-path': 'polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%)' }
];

const beams = [
  { width: '200%', height: '2px', top: '30%', left: '-50%', right: '', bottom: '', delay: '0s' },
  { width: '200%', height: '2px', top: '70%', left: '-50%', right: '', bottom: '', delay: '1s' }
];

// 定义样式映射类型
type StyleMap = Record<string, string>;

// 定义装饰元素类型
interface DecorativeElement {
  width?: string;
  height?: string;
  top?: string;
  left?: string;
  right?: string;
  bottom?: string;
  'delay-float'?: string;
  'delay-rotate'?: string;
  delay?: string;
  clipPath?: string;
  'clip-path'?: string;
  opacity?: string;
  background?: string;
  borderRadius?: string;
  border?: string;
  transform?: string;
  animation?: string;
  filter?: string;
  boxShadow?: string;
}

// 装饰元素数据

const balls: DecorativeElement[] = [
  { width: '45px', height: '45px', top: '15%', left: '', right: '15%', bottom: '', delay: '0s' },
  { width: '30px', height: '30px', top: '', left: '', right: '20%', bottom: '20%', delay: '0.4s' },
  { width: '55px', height: '55px', top: '45%', left: '12%', right: '', bottom: '', delay: '0.8s' },
  { width: '25px', height: '25px', top: '25%', left: '18%', right: '', bottom: '', delay: '1.2s' },
  { width: '40px', height: '40px', top: '', left: '', right: '25%', bottom: '35%', delay: '1.6s' },
  { width: '35px', height: '35px', top: '65%', left: '', right: '15%', bottom: '', delay: '0.6s' },
  { width: '50px', height: '50px', top: '', left: '15%', right: '', bottom: '15%', delay: '1.4s' }
];



// 通用函数：生成样式对象
function generateStyle(item: Record<string, string>): StyleMap {
  const style: StyleMap = {};
  for (const [key, value] of Object.entries(item)) {
    style[`--${key}`] = value;
  }
  return style;
}

// 缓存粒子样式，避免每次渲染都重新生成
const particleStylesCache = ref<StyleMap[]>([]);
const progressParticleStylesCache = ref<StyleMap[]>([]);
const successParticleStylesCache = ref<StyleMap[]>([]);
const successParticleBgStylesCache = ref<StyleMap[]>([]);
const successSparkleStylesCache = ref<StyleMap[]>([]);
const confettiLeftStylesCache = ref<StyleMap[]>([]);
const confettiRightStylesCache = ref<StyleMap[]>([]);

// 通用彩带生成器
type Side = 'left' | 'right';
const pushConfetti = (side: Side, count: number, angleStart: number, angleSpan: number, cache: StyleMap[]) => {
  for (let i = 0; i < count; i++) {
    const size = Math.random() * 10 + 5;
    const angle = angleStart + Math.random() * angleSpan;
    const distance = 400 + Math.random() * 300;
    const endX = distance * Math.cos(angle * Math.PI / 180);
    const endY = distance * Math.sin(angle * Math.PI / 180);
    const delay = Math.random() * 3;
    const duration = 4 + Math.random() * 2;
    const rotation = Math.random() * 720;
    const hue = Math.floor(Math.random() * 360);
    const saturation = Math.floor(Math.random() * 30) + 70;
    const lightness = Math.floor(Math.random() * 20) + 50;

    const pos = `${Math.random() * 10}%`;
    const style: StyleMap = {
      width: `${size}px`,
      height: `${size}px`,
      bottom: '0%',
      animationDuration: `${duration}s`,
      animationDelay: `${delay}s`,
      background: `hsl(${hue}, ${saturation}%, ${lightness}%)`,
      opacity: '0',
      borderRadius: Math.random() > 0.5 ? '50%' : '0',
      '--end-x': `${endX}px`,
      '--end-y': `${endY}px`,
      '--end-rotation': `${rotation}deg`,
    };

    if (side === 'left') style.left = pos; else style.right = pos;
    cache.push(style);
  }
};

// 单独初始化彩带样式的函数
const initConfettiStyles = (): void => {
  confettiLeftStylesCache.value = [];
  confettiRightStylesCache.value = [];
  pushConfetti('left', 60, 15, 60, confettiLeftStylesCache.value);   // 15°~75°
  pushConfetti('right', 60, 105, 60, confettiRightStylesCache.value); // 105°~165°
};

// 通用：把 N 个样式 push 到某个 cache
const fillStyles = (cacheRef: { value: StyleMap[] }, count: number, gen: (i: number) => StyleMap) => {
  cacheRef.value = [];
  for (let i = 0; i < count; i++) cacheRef.value.push(gen(i));
};

// 初始化粒子样式
const initParticleStyles = (): void => {
  fillStyles(particleStylesCache, 20, (): StyleMap => {
    const size = Math.random() * 5 + 2;
    return {
      width: `${size}px`,
      height: `${size}px`,
      left: `${Math.random() * 100}%`,
      top: `${Math.random() * 100}%`,
      animationDuration: `${Math.random() * 10 + 10}s`,
      animationDelay: `${Math.random() * 5}s`,
    };
  });

  fillStyles(progressParticleStylesCache, 8, (): StyleMap => {
    const size = Math.random() * 4 + 2;
    return {
      width: `${size}px`,
      height: `${size}px`,
      animationDuration: `${Math.random() * 1 + 0.5}s`,
      animationDelay: `${Math.random() * 2}s`,
      left: `${Math.random() * 100}%`,
    };
  });

  fillStyles(successParticleStylesCache, 20, (i): StyleMap => {
    const angle = (i / 20) * Math.PI * 2;
    const distance = 60 + Math.random() * 40; // 增加飞行距离
    const size = Math.random() * 6 + 3; // 增加大小
    return {
      width: `${size}px`,
      height: `${size}px`,
      animationDuration: `${Math.random() * 2 + 1}s`, // 增加持续时间
      animationDelay: `${Math.random() * 0.3 + 0.2}s`, // 修改触发延迟为0.2到0.5秒
      transform: `translate(${Math.cos(angle) * distance}px, ${Math.sin(angle) * distance}px)`,
    };
  });

  fillStyles(successParticleBgStylesCache, 30, (): StyleMap => {
    const size = Math.random() * 6 + 3;
    return {
      width: `${size}px`,
      height: `${size}px`,
      left: `${Math.random() * 100}%`,
      top: `${Math.random() * 100}%`,
      animationDuration: `${Math.random() * 15 + 10}s`,
      animationDelay: `${Math.random() * 5}s`,
      background: `hsl(${Math.random() * 40 + 190}, 70%, 60%)`,
    };
  });

  fillStyles(successSparkleStylesCache, 16, (i): StyleMap => {
    const angle = (i / 16) * Math.PI * 2;
    const distance = 100 + Math.random() * 40; // 再增加20飞行距离
    const size = Math.random() * 6 + 4;
    const rotation = Math.random() * 360;
    const tx = Math.cos(angle) * distance;
    const ty = Math.sin(angle) * distance;

    return {
      width: `${size}px`,
      height: `${size}px`,
      animationDuration: `${Math.random() * 1.5 + 1.5}s`, // 稍微缩短持续时间，加快速度
      animationDelay: `${Math.random() * 0.7 + 0.8}s`, // 延迟调整为0.8到1.5秒
      // 起点交给 keyframes 的 0% 就好，不必写 transform 起始值
      '--tx': `${tx}px`,
      '--ty': `${ty}px`,
      '--rotation': `${rotation}deg`,
    };
  });

  // 彩带
  initConfettiStyles();
};

// 获取缓存的粒子样式
const getParticleStyle = (index: number): StyleMap => {
  return particleStylesCache.value[index] || {};
};

const getProgressParticleStyle = (index: number): StyleMap => {
  return progressParticleStylesCache.value[index] || {};
};

const getSuccessParticleStyle = (index: number): StyleMap => {
  return successParticleStylesCache.value[index] || {};
};

const getConfettiLeftStyle = (index: number): StyleMap => {
  return confettiLeftStylesCache.value[index] || {};
};

const getConfettiRightStyle = (index: number): StyleMap => {
  return confettiRightStylesCache.value[index] || {};
};

const getSuccessParticleBgStyle = (index: number): StyleMap => {
  return successParticleBgStylesCache.value[index] || {};
};

const getSuccessSparkleStyle = (index: number): StyleMap => {
  return successSparkleStylesCache.value[index] || {};
};

// 验证结束天输入 - 只允许整数
const validateEndDay = (event: Event): void => {
  const target = event.target as HTMLInputElement;
  let value = String(target.value || ''); // 确保value始终是字符串
  
  // 只允许输入数字
  value = value.replace(/[^0-9]/g, '');
  
  // 确保是正整数
  if (value && parseInt(value, 10) < 0) {
    value = '';
  }
  
  // 如果值被修改了，更新输入框
  if (target.value !== value) {
    endDay.value = value; // 确保endDay始终是字符串
  }
};

const generateReport = async (): Promise<void> => {
  if (!projectNumber.value.trim()) return;
  
  isGenerating.value = true;
  progress.value = 0;
  reportGenerated.value = false;
  error.value = '';
  reportData.value = null;
  
  // 立即开始进度条动画
  progressInterval = setInterval(() => {
    // 如果进度小于90%，继续增加
    if (progress.value < 90) {
      progress.value += Math.random() * 3;
    }
  }, 400);
  
  try {
    // 准备请求数据
    const requestData: Record<string, string | number> = { project_code: projectNumber.value.trim() };
    
    // 如果用户输入了结束天，添加到请求数据中
    if (endDay.value) {
      // 确保结束天是有效的正整数
      const endDayNum = parseInt(endDay.value, 10);
      if (!isNaN(endDayNum) && endDayNum > 0) {
        requestData.end_day = endDayNum;
      }
    }
    
    // 调试信息：打印请求数据
    console.log('发送到后端的数据:', requestData);
    
    // 尝试连接后端API
    const response = await fetch(
      `${import.meta.env.VITE_GLOB_API_URL_REPORT}/project-report/execute`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          disease: selectedDisease.value,
          language: selectedLanguage.value,
          function: 'generate',
          content: requestData
        }),
      }
    );
    
    if (!response.ok) {
      throw new Error(`服务器响应错误: ${response.status}`);
    }
    
    // 后端响应成功，完成进度条
    clearInterval(progressInterval);
    
    // 获取后端返回的JSON数据
    const data: ReportResponse = await response.json();
    reportData.value = data;
    
    // 快速完成剩余进度
    completeInterval = setInterval(() => {
      progress.value += 5;
      if (progress.value >= 100) {
        clearInterval(completeInterval);
        completeInterval = null;
        progress.value = 100;
        
        setTimeout(() => {
          isGenerating.value = false;
          reportGenerated.value = true;
          // 触发彩带特效
          showConfetti.value = true;
          // 强制重新触发动画
          setTimeout(() => {
            const confettiContainer = document.querySelector('.confetti-container');
            if (confettiContainer) {
              confettiContainer.classList.remove('show-animation');
              // 触发重排
              void confettiContainer.offsetWidth;
              confettiContainer.classList.add('show-animation');
            }
          }, 50);
          // 自动下载Word文档
          autoDownloadWordDocument();
          // 自动滚动到结果区域
          nextTick(() => {
            if (resultSectionRef.value) {
              resultSectionRef.value.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
          });
        }, 500);
      }
    }, 100);
    
  } catch (err) {
    console.error('生成报告失败:', err);
    
    // 发生错误，停止进度条并显示错误
    clearInterval(progressInterval);
    
    // 进度条停在当前位置
    setTimeout(() => {
      isGenerating.value = false;
      error.value = '无法连接到报告生成服务，请确保后端服务已启动。';
    }, 500);
  }
};

const retryWithCorrection = (): void => {
  // 自动修正实验编号格式（将小写p替换为大写P）
  if (projectNumber.value) {
    projectNumber.value = projectNumber.value.replace(/p/g, 'P');
  }
  
  // 清除错误状态，重新尝试生成报告
  error.value = '';
  progress.value = 0;
  
  // 如果有实验编号，自动开始生成
  if (projectNumber.value.trim()) {
    generateReport();
  }
};

// 下载Excel文件
const downloadFile = (type: 'final' | 'details'): void => {
  if (!reportData.value) return;
  
  const file = type === 'final' ? reportData.value.files.final_excel : reportData.value.files.details_excel;
  
  if (file.exists) {
    // 使用完整的URL路径，包括API基础URL
    const fullUrl = `${import.meta.env.VITE_GLOB_API_URL_REPORT}${file.url}`;
    const link = document.createElement('a');
    link.href = fullUrl;
    link.download = file.name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } else {
    alert(`${type === 'final' ? '终版' : '明细'}Excel文件不存在，请重新生成报告`);
  }
};

// 下载图片压缩包
const downloadImagesZip = (): void => {
  if (!reportData.value || !reportData.value.files.images_zip?.exists) {
    alert('图片压缩包不存在，请重新生成报告');
    return;
  }
  
  // 使用完整的URL路径，包括API基础URL
  const fullUrl = `${import.meta.env.VITE_GLOB_API_URL_REPORT}${reportData.value.files.images_zip.url}`;
  const link = document.createElement('a');
  link.href = fullUrl;
  link.download = reportData.value.files.images_zip.name;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// 下载Word文档
const downloadWordDocument = (): void => {
  if (reportData.value && reportData.value.files.word_document.exists) {
    // 使用完整的URL路径，包括API基础URL
    const fullUrl = `${import.meta.env.VITE_GLOB_API_URL_REPORT}${reportData.value.files.word_document.url}`;
    const link = document.createElement('a');
    link.href = fullUrl;
    link.download = reportData.value.files.word_document.name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } else {
    alert('Word文档不存在，请重新生成报告');
  }
};

// 自动下载Word文档
const autoDownloadWordDocument = (): void => {
  // 延迟1秒后自动下载，让用户先看到成功界面
  setTimeout(() => {
    downloadWordDocument();
  }, 1000);
};

const downloadReport = (): void => {
  // 使用Blob URL下载报告
  if (reportBlobUrl.value) {
    const link = document.createElement('a');
    link.href = reportBlobUrl.value;
    // 设置自定义文件名，避免乱码
    link.download = `${projectNumber.value}_项目报告.docx`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    // 注意：这里不释放URL对象，以便用户可以多次下载
  } else {
    // 如果没有Blob URL，提示用户重新生成报告
    alert('报告文件已过期，请重新生成报告');
    resetForm();
  }
};

// 自动下载报告
const autoDownloadReport = (): void => {
  // 延迟1秒后自动下载，让用户先看到成功界面
  setTimeout(() => {
    downloadReport();
  }, 1000);
};

const resetForm = (): void => {
  projectNumber.value = '';
  endDay.value = '';
  reportGenerated.value = false;
  showConfetti.value = false;
  error.value = '';
  progress.value = 0;
  reportData.value = null;
  
  // 清理计时器
  if (progressInterval) {
    clearInterval(progressInterval);
    progressInterval = null;
  }
  if (completeInterval) {
    clearInterval(completeInterval);
    completeInterval = null;
  }
  
  // 释放Blob URL对象
  if (reportBlobUrl.value) {
    URL.revokeObjectURL(reportBlobUrl.value);
    reportBlobUrl.value = '';
  }
  // 重置彩带特效缓存，以便下次可以重新触发
  confettiLeftStylesCache.value = [];
  confettiRightStylesCache.value = [];
  // 重新初始化彩带样式
  setTimeout(() => {
    initConfettiStyles();
  }, 100);
};

// 监听路由变化，在离开页面时重置彩带特效
const route = useRoute();

// 组件卸载时重置彩带特效和清理计时器
onBeforeUnmount((): void => {
  showConfetti.value = false;
  // 清理计时器，防止内存泄漏
  if (progressInterval) {
    clearInterval(progressInterval);
    progressInterval = null;
  }
  if (completeInterval) {
    clearInterval(completeInterval);
    completeInterval = null;
  }
  // 释放Blob URL，避免内存泄漏
  if (reportBlobUrl.value) {
    URL.revokeObjectURL(reportBlobUrl.value);
    reportBlobUrl.value = '';
  }
});

// 组件挂载时初始化粒子样式
onMounted((): void => {
  initParticleStyles();
});

// 监听路由变化，重置彩带特效
watch((): string => route.path, (newPath: string, oldPath: string): void => {
  if (newPath !== oldPath) {
    showConfetti.value = false;
  }
});
</script>

<style scoped>
.report-generator-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 2.5rem;
  border-radius: var(--radius);
  background-color: hsl(var(--card));
  color: hsl(var(--foreground));
  box-shadow: 0 10px 25px -5px hsl(var(--foreground) / 0.1), 0 8px 10px -6px hsl(var(--foreground) / 0.1);
  position: relative;
  overflow: hidden;
}

/* 装饰性背景元素 */
.decorative-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}

.floating-shape {
  position: absolute;
  border-radius: 50%;
  background: hsl(var(--primary) / 0.05);
  animation: float 8s ease-in-out infinite, rotate 20s linear infinite;
  will-change: transform;
  width: var(--width, 80px);
  height: var(--height, 80px);
  top: var(--top, 10%);
  left: var(--left, 5%);
  right: var(--right, auto);
  bottom: var(--bottom, auto);
  /* 两段动画各自的延迟，与老版一致 */
  animation-delay: var(--delay-float, 0s), var(--delay-rotate, 0s);
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

/* 使用 rotate 替代 */

/* 浮动粒子 */
.floating-particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.particle {
  position: absolute;
  border-radius: 50%;
  background: hsl(var(--primary));
  animation: background-float-particle linear infinite;
  opacity: 0;
  will-change: transform, opacity;
}

@keyframes background-float-particle {
  0% {
    transform: translateY(0) translateX(0);
    opacity: 0;
  }
 10% {
    opacity: 1;
  }
 90% {
    opacity: 1;
  }
 100% {
    transform: translateY(-100vh) translateX(20px);
    opacity: 0;
  }
}

.report-header {
  text-align: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid hsl(var(--border));
  position: relative;
  z-index: 1;
}

.header-icon {
  margin-bottom: 0.5rem;
  position: relative;
  display: inline-block;
}

.icon-text {
  font-size: 2.5rem;
  position: relative;
  z-index: 1;
  animation: bounce 2s ease-in-out infinite;
  --bounce-distance: -10px;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(var(--bounce-distance, -10px));
  }
}

@keyframes pulse {
  0%, 100% {
    transform: var(--pulse-transform, scale(1));
    opacity: var(--pulse-start-opacity, 1);
  }
  50% {
    transform: var(--pulse-mid-transform, scale(1.1));
    opacity: var(--pulse-mid-opacity, 1);
  }
}

.icon-decoration {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 120%;
  height: 120%;
  border-radius: 50%;
  background: radial-gradient(circle, hsl(var(--primary) / 0.1) 0%, transparent 70%);
  transform: translate(-50%, -50%);
  animation: pulse 3s ease-in-out infinite;
  --pulse-transform: translate(-50%, -50%) scale(0.8);
  --pulse-mid-transform: translate(-50%, -50%) scale(1.2);
  --pulse-start-opacity: 0.5;
  --pulse-mid-opacity: 0.2;
}

/* 使用 pulse 替代 */

.report-title {
  font-size: 1.85rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
  color: hsl(var(--foreground));
  background: linear-gradient(90deg, hsl(var(--foreground)), hsl(var(--primary)));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  display: inline-block;
}

.report-description {
  font-size: 1.05rem;
  color: hsl(var(--muted-foreground));
}

.report-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  position: relative;
  z-index: 1;
}

.input-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: flex;
  gap: 1rem;
  margin-top: 0.75rem;
}

.project-number-group {
  flex: 7;
}

.end-day-group {
  flex: 2;
}

.disease-type-group {
  flex: 5;
}

.language-group {
  flex: 3;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-weight: 500;
  font-size: 0.9rem;
  color: hsl(var(--foreground));
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.label-icon {
  font-size: 1rem;
}

.input-wrapper {
  position: relative;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1.25rem;
  border-radius: calc(var(--radius) - 2px);
  border: 1px solid hsl(var(--input));
  background-color: hsl(var(--input-background));
  color: hsl(var(--foreground));
  font-size: 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
  position: relative;
  z-index: 1;
}

.form-input:focus {
  outline: none;
  border-color: hsl(var(--primary));
  box-shadow: 0 0 0 2px hsl(var(--primary) / 0.2);
}

.form-input::placeholder {
  color: hsl(var(--input-placeholder));
}

.input-decoration {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 2px;
  width: 0;
  background: hsl(var(--primary));
  transition: width 0.3s ease;
  border-radius: 2px;
}

.input-glow {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: calc(var(--radius) - 2px);
  background: radial-gradient(circle at center, hsl(var(--primary) / 0.1) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.form-input:focus ~ .input-decoration {
  width: 100%;
}

.form-input:focus ~ .input-glow {
  opacity: 1;
}

/* 选择框样式 */
.disease-select {
  width: 100%;
  font-size: 18px;
}

.language-switch {
  display: flex;
  align-items: center;
  gap: 8px;
}

.language-switch span {
  font-size: 14px;
  color: #666;
  transition: color 0.3s ease;
}

.language-switch span.active {
  color: #1890ff;
  font-weight: 500;
}

.button-container {
  display: flex;
  justify-content: center;
  margin-bottom: 0.1rem;
}

.generate-button {
  padding: 0.875rem 2.5rem;
  border-radius: calc(var(--radius) - 2px);
  border: none;
  background: linear-gradient(135deg, hsl(var(--primary)) 0%, hsl(var(--primary) / 0.8) 100%);
  color: hsl(var(--primary-foreground));
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.generate-button:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 10px 20px hsl(var(--primary) / 0.3);
}

.generate-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.button-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  position: relative;
  z-index: 1;
}

.button-icon {
  font-size: 1.2rem;
}

.button-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 50%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.6s ease;
}

.generate-button:hover .button-shine {
  left: 100%;
}

.loading-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid hsl(var(--primary-foreground));
  border-top-color: transparent;
  border-radius: 50%;
  animation: rotate 0.8s linear infinite;
}

/* 使用 rotate 替代 */

/* 进度条区域，点击生成后才显示 */
.progress-section {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding: 2rem;
  padding-top: 1.5rem;
  border-radius: calc(var(--radius) - 2px);
  background-color: hsl(var(--accent));
  border: 1px solid hsl(var(--border));
  position: relative;
  overflow: hidden;
  opacity: 0.7;
  transition: opacity 0.3s ease;
  margin-top: 0.1rem;
}

.progress-section.active {
  opacity: 1;
}

.progress-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.25rem;
}

.progress-icon {
  font-size: 1.5rem;
  animation: rotate 3s linear infinite;
}

@keyframes rotate {
  to {
    transform: rotate(360deg);
  }
}

.progress-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: hsl(var(--foreground));
  margin: 0;
}

.progress-bar-container {
  height: 1rem;
  border-radius: calc(var(--radius) - 2px);
  background-color: hsl(var(--muted));
  overflow: hidden;
  position: relative;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, hsl(var(--primary)) 0%, hsl(var(--primary) / 0.8) 100%);
  border-radius: calc(var(--radius) - 2px);
  transition: width 0.3s ease;
  will-change: width;
}

.progress-glow {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: linear-gradient(90deg, transparent, hsl(var(--primary) / 0.4), transparent);
  border-radius: calc(var(--radius) - 2px);
  transition: width 0.3s ease;
  animation: glow 1.5s infinite;
  will-change: width, transform;
}

.progress-particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.progress-particle {
  position: absolute;
  top: 50%;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: hsl(var(--primary));
  transform: translateY(-50%);
  animation: progress-bar-particle 1.5s linear infinite;
  opacity: 0;
  will-change: transform, opacity;
}

@keyframes progress-bar-particle {
  0% {
    transform: translateY(-50%) translateX(-10px);
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
  100% {
    transform: translateY(-50%) translateX(10px);
    opacity: 0;
  }
}

@keyframes glow {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.progress-text {
  font-size: 0.875rem;
  color: hsl(var(--muted-foreground));
  text-align: center;
  font-weight: 500;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  opacity: 0.5;
  transition: opacity 0.3s ease;
  position: relative;
}

.step-item.active {
  opacity: 1;
}

.step-icon {
  font-size: 1.25rem;
}

.step-text {
  font-size: 0.75rem;
  color: hsl(var(--muted-foreground));
  text-align: center;
}

.step-indicator {
  position: absolute;
  bottom: -15px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: hsl(var(--primary));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.step-item.active .step-indicator {
  opacity: 1;
  animation: bounce 1s ease-in-out infinite;
  --bounce-distance: -5px;
}

/* 使用 bounce 替代 */

/* 新增动态装饰元素样式 */
.floating-orb {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, hsl(var(--primary) / 0.3), hsl(var(--primary) / 0.1));
  filter: blur(2px);
  animation: float 15s ease-in-out infinite;
  will-change: transform;
  width: var(--width, 100px);
  height: var(--height, 100px);
  top: var(--top, 15%);
  left: var(--left, 10%);
  right: var(--right, auto);
  bottom: var(--bottom, auto);
  animation-delay: var(--delay, 0s);
}

/* 使用 float 替代，通过不同的animation-duration和animation-timing-function来调整效果 */

.geometric-shape {
  position: absolute;
  background: hsl(var(--primary) / 0.05);
  animation: rotate 20s linear infinite;
  will-change: transform;
  width: var(--width, 60px);
  height: var(--height, 60px);
  top: var(--top, 25%);
  left: var(--left, auto);
  right: var(--right, auto);
  bottom: var(--bottom, auto);
  animation-delay: var(--delay, 0s);
  clip-path: var(--clip-path, polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%));
}

/* 使用 rotate 替代 */

.light-beam {
  position: absolute;
  background: linear-gradient(90deg, transparent, hsl(var(--primary) / 0.1), transparent);
  transform-origin: center;
  animation: beam-sweep 10s ease-in-out infinite;
  will-change: transform, opacity;
  width: var(--width, 200%);
  height: var(--height, 2px);
  top: var(--top, 30%);
  left: var(--left, -50%);
  right: var(--right, auto);
  bottom: var(--bottom, auto);
  animation-delay: var(--delay, 0s);
}

@keyframes beam-sweep {
  0%, 100% {
    transform: rotate(0deg);
    opacity: 0.3;
  }
  50% {
    transform: rotate(10deg);
    opacity: 0.6;
  }
}

.error-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  border-radius: calc(var(--radius) - 2px);
  background-color: hsl(var(--destructive) / 0.1);
  border: 1px solid hsl(var(--destructive) / 0.2);
}

.error-icon {
  font-size: 2rem;
  /* 移除晃动动画 */
}

.error-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: hsl(var(--destructive));
  margin: 0;
}

.error-message {
  font-size: 1rem;
  color: #ff3333; /* 更明显的错误提示颜色 */
  text-align: center;
  margin: 0;
  font-weight: 500; /* 增加字体粗细 */
}

.error-actions {
  display: flex;
  justify-content: center;
}

.retry-button {
  padding: 0.625rem 1.75rem;
  border-radius: calc(var(--radius) - 2px);
  border: none;
  background-color: hsl(var(--destructive));
  color: hsl(var(--destructive-foreground));
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.retry-button:hover {
  background-color: hsl(var(--destructive) / 0.9);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px hsl(var(--destructive) / 0.3);
}

.result-section {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
  padding: 2rem;
  padding-top: 3.5rem;
  border-radius: calc(var(--radius) - 2px);
  background-color: hsl(var(--accent));
  border: 1px solid hsl(var(--border));
  animation: result-section-appear 0.8s ease-out;
  position: relative;
  overflow: hidden;
}

/* 为成功结果区域添加动态背景效果 */
.result-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}

/* 添加全屏彩带特效 */
.confetti-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 9999;
  overflow: hidden;
}

.confetti-left {
  position: absolute;
  left: 0;
  bottom: 0;
  animation: none;
  opacity: 0;
}

.confetti-right {
  position: absolute;
  right: 0;
  bottom: 0;
  animation: none;
  opacity: 0;
}

/* 当showConfetti为true时应用动画 */
.confetti-container.show-animation .confetti-left,
.confetti-container.show-animation .confetti-right {
  animation: confetti-simple 6s cubic-bezier(0.05, 0.5, 0.25, 1) forwards;
}

@keyframes confetti-simple {
  0% {
    transform: translate(0, 0) rotate(0deg);
    opacity: 0;
  }
  5% {
    opacity: 0.8;
  }
  95% {
    opacity: 0.8;
  }
  100% {
    transform: translate(var(--end-x), calc(-1 * var(--end-y))) rotate(var(--end-rotation));
    opacity: 0;
  }
}

/* 添加上浮小球效果 */
.success-floating-particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
}

.success-particle-bg {
  position: absolute;
  border-radius: 50%;
  animation: success-bg-particle linear infinite;
  opacity: 0;
  will-change: transform, opacity;
}

@keyframes success-bg-particle {
  0% {
    transform: translateY(0) translateX(0);
    opacity: 0;
  }
 10% {
    opacity: 0.4;
  }
 90% {
    opacity: 0.4;
  }
 100% {
    transform: translateY(-100vh) translateX(20px);
    opacity: 0;
  }
}

/* 使用 rotate 替代 */

/* 添加浮动球 */
.result-section .floating-ball {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, hsla(210, 70%, 60%, 0.05), hsla(240, 70%, 60%, 0.02));
  animation: float 12s ease-in-out infinite;
  z-index: 0;
  will-change: transform;
  width: var(--width, 40px);
  height: var(--height, 40px);
  top: var(--top, 20%);
  left: var(--left, auto);
  right: var(--right, auto);
  bottom: var(--bottom, auto);
  animation-delay: var(--delay, 0s);
}

/* 使用 float 替代，通过不同的animation-duration和animation-timing-function来调整效果 */



@keyframes result-section-appear {
  0% {
    transform: translateY(20px);
    opacity: 0;
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}

.result-header {
  text-align: center;
}

.success-animation {
  position: relative;
  display: inline-block;
  margin-bottom: 1rem;
}

.success-icon-container {
  position: relative;
  display: inline-block;
  margin-bottom: 1rem;
  animation: success-bounce 0.8s ease-out;
  --start-rotation: -10deg;
  --mid-scale: 1.3;
  --mid-rotation: 5deg;
}

@keyframes success-bounce {
  0% {
    transform: scale(0) rotate(var(--start-rotation, -10deg));
    opacity: 0;
  }
  50% {
    transform: scale(var(--mid-scale, 1.3)) rotate(var(--mid-rotation, 5deg));
  }
  100% {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
}

.success-icon {
  font-size: 3.5rem;
  position: relative;
  z-index: 3;
  animation: success-bounce 1s ease-out, success-icon-glow 4s ease-in-out infinite;
  filter: drop-shadow(0 0 20px hsl(var(--success) / 0.9)) drop-shadow(0 0 10px hsl(var(--primary) / 0.8));
  transform-style: preserve-3d;
  /* 使用圆形图标 */
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, hsl(var(--success)), hsl(var(--primary)));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2.5rem;
  /* 确保保持圆形 */
  aspect-ratio: 1/1;
  object-fit: contain;
  overflow: hidden;
  --start-rotation: 0deg;
  --mid-scale: 1.4;
  --mid-rotation: 10deg;
}

/* 使用 success-bounce 替代，通过不同的CSS变量来调整效果 */

@keyframes success-icon-glow {
  0%, 100% {
    box-shadow: 0 0 15px hsl(var(--success) / 0.8), 0 0 30px hsl(var(--primary) / 0.6);
  }
  50% {
    box-shadow: 0 0 25px hsl(var(--success) / 1), 0 0 50px hsl(var(--primary) / 0.8);
  }
}

.success-icon-bg {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 150%;
    height: 150%;
    border-radius: 50%;
    background: radial-gradient(circle, hsla(120, 70%, 60%, 0.7) 0%, hsla(200, 70%, 60%, 0.5) 30%, transparent 70%);
    transform: translate(-50%, -50%);
    z-index: 1;
    animation: pulse 2.4s ease-in-out infinite;
    --pulse-transform: translate(-50%, -50%) scale(0.7);
    --pulse-mid-transform: translate(-50%, -50%) scale(1.3);
    --pulse-start-opacity: 0.9;
    --pulse-mid-opacity: 0.6;
    box-shadow: 0 0 40px hsla(120, 70%, 60%, 0.9), inset 0 0 40px hsla(200, 70%, 60%, 0.6);
    /* 确保保持圆形 */
    aspect-ratio: 1/1;
    filter: blur(3px);
  }

/* 使用 pulse 替代 */





.success-particles {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 100%;
  transform: translate(-50%, -50%);
}

.success-particle {
  position: absolute;
  top: 50%;
  left: 50%;
  border-radius: 50%;
  background: hsl(var(--success));
  opacity: 0;
  animation: success-particle-effect 1.5s ease-out forwards;
  will-change: transform, opacity;
}

@keyframes success-particle-effect {
  0% {
    transform: translate(0, 0);
    opacity: 1;
  }
  100% {
    opacity: 0;
  }
}

.success-sparkles {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 100%;
  transform: translate(-50%, -50%);
}

.success-sparkle {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 8px;
  height: 8px;
  background: linear-gradient(45deg, hsl(var(--success)), hsl(var(--primary)));
  clip-path: polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%);
  opacity: 0;
  animation: success-sparkle-effect 2s ease-out forwards;
  will-change: transform, opacity;
}

@keyframes success-sparkle-effect {
  0% {
    transform: translate(0, 0) scale(0) rotate(0deg);
    opacity: 0;
  }
  20% {
    opacity: 1;
  }
  80% {
    opacity: 1;
  }
  100% {
    transform: translate(var(--tx), var(--ty)) scale(1) rotate(var(--rotation));
    opacity: 0;
  }
}



.result-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: hsl(var(--foreground));
  animation: fade-in-down 0.6s ease-out 0.3s both;
}

@keyframes fade-in-down {
  0% {
    transform: translateY(var(--start-y, -10px));
    opacity: 0;
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}

.result-description {
  font-size: 1rem;
  color: hsl(var(--muted-foreground));
  animation: fade-in-down 0.6s ease-out 0.5s both;
}

/* 使用 fade-in-down 替代 */

.result-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  animation: fade-in-up 0.6s ease-out 0.7s both;
}

.details-row {
  display: flex;
  gap: 1rem;
}

@keyframes fade-in-up {
  0% {
    transform: translateY(var(--start-y, 10px));
    opacity: 0;
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}

.detail-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  border-radius: calc(var(--radius) - 2px);
  background-color: hsl(var(--card));
  border: 1px solid hsl(var(--border));
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.detail-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px hsl(var(--foreground) / 0.1);
}

.detail-icon {
  font-size: 1.25rem;
}

.detail-text {
  flex: 1;
}

.detail-label {
  font-size: 0.8rem;
  color: hsl(var(--muted-foreground));
}

.detail-value {
  font-size: 0.9rem;
  font-weight: 500;
  color: hsl(var(--foreground));
}

.detail-status {
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

.result-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  animation: fade-in-up 0.6s ease-out 0.9s both;
}

/* 使用 fade-in-up 替代 */

.action-button {
  padding: 0.875rem 1.75rem;
  border-radius: calc(var(--radius) - 2px);
  border: none;
  background-color: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
  font-weight: 500;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  position: relative;
  overflow: hidden;
}

.action-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 20px hsl(var(--primary) / 0.3);
}

.action-button.secondary {
  background-color: hsl(var(--secondary));
  color: hsl(var(--secondary-foreground));
  border: 1px solid hsl(var(--border));
}

.action-button.secondary:hover {
  background-color: hsl(var(--accent));
  box-shadow: 0 10px 20px hsl(var(--foreground) / 0.1);
}

@media (max-width: 640px) {
  .report-generator-container {
    padding: 1.5rem;
    max-width: 100%;
  }
  
  .report-title {
    font-size: 1.5rem;
  }
  
  .result-actions {
    flex-direction: column;
  }
  
  .action-button {
    width: 100%;
  }
  
  .progress-steps {
    flex-wrap: wrap;
    gap: 0.75rem;
  }
  
  .step-item {
    flex: 1 0 30%;
  }
  
  .error-actions {
    flex-direction: column;
  }
  
  .retry-button {
    width: 100%;
  }
}
.detail-status {
  font-size: 0.8rem;
  margin-top: 4px;
  font-weight: 500;
}

.status-exists {
  color: #10b981;
}

.status-missing {
  color: #ef4444;
}
</style>