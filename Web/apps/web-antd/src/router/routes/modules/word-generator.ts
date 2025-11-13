import type { RouteRecordRaw } from 'vue-router';

import { $t } from '#/locales';

const routes: RouteRecordRaw[] = [
  {
    meta: {
      icon: 'mdi:file-document-outline',
      keepAlive: true,
      order: 1,
      title: 'Word方案生成器',
    },
    name: 'WordGenerator',
    path: '/word-generator',
    redirect: '/word-generator/index',
    children: [
      {
        name: 'WordGeneratorIndex',
        path: '/word-generator/index',
        component: () => import('#/views/word-generator/index.vue'),
        meta: {
          affixTab: true,
          affixTabOrder: 1,
          icon: 'mdi:file-document-edit-outline',
          title: '项目方案生成',
          keepAlive: true,
        },
      },
    ],
  },
];

export default routes;