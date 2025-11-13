<script lang="ts" setup>
import { computed, onMounted, onBeforeUnmount } from 'vue';

import { useAntdDesignTokens } from '@vben/hooks';
import { preferences, usePreferences } from '@vben/preferences';

import { App, ConfigProvider, theme } from 'ant-design-vue';

import { antdLocale } from '#/locales';

defineOptions({ name: 'App' });

const { isDark } = usePreferences();
const { tokens } = useAntdDesignTokens();

const tokenTheme = computed(() => {
  const algorithm = isDark.value
    ? [theme.darkAlgorithm]
    : [theme.defaultAlgorithm];

  // antd 紧凑模式算法
  if (preferences.app.compact) {
    algorithm.push(theme.compactAlgorithm);
  }

  return {
    algorithm,
    token: tokens,
  };
});

/**
 * 清理所有缓存
 */
function clearAllCache() {
  // 清理 preferences 缓存
  const preferencesKeys = ['preferences', 'preferences-locale', 'preferences-theme'];
  preferencesKeys.forEach(key => {
    localStorage.removeItem(key);
  });
  
  // 清理所有以项目前缀开头的缓存
  const namespace = `${import.meta.env.VITE_APP_NAMESPACE}-${import.meta.env.VITE_APP_VERSION}-${import.meta.env.PROD ? 'prod' : 'dev'}`;
  const keysToRemove: string[] = [];
  
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key && key.startsWith(namespace)) {
      keysToRemove.push(key);
    }
  }
  
  keysToRemove.forEach(key => {
    localStorage.removeItem(key);
  });
  
  // 清理 sessionStorage
  sessionStorage.clear();
}

/**
 * 处理页面刷新事件
 */
function handleBeforeUnload(event: BeforeUnloadEvent) {
  // 页面刷新时清理缓存
  clearAllCache();
}

onMounted(() => {
  // 监听页面刷新事件
  window.addEventListener('beforeunload', handleBeforeUnload);
});

onBeforeUnmount(() => {
  // 移除事件监听
  window.removeEventListener('beforeunload', handleBeforeUnload);
});
</script>

<template>
  <ConfigProvider :locale="antdLocale" :theme="tokenTheme">
    <App>
      <RouterView />
    </App>
  </ConfigProvider>
</template>
