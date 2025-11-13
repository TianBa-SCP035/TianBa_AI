import type { RouteRecordRaw } from 'vue-router';

import { $t } from '#/locales';

const routes: RouteRecordRaw[] = [
  {
    meta: {
      icon: 'mdi:file-chart-outline',
      keepAlive: true,
      order: 2,
      title: 'Word报告生成器',
    },
    name: 'ReportGenerator',
    path: '/Report-generator',
    redirect: '/Report-generator/index',
    children: [
      {
        name: 'ReportGeneratorIndex',
        path: '/Report-generator/index',
        component: () => import('#/views/Report-generator/index.vue'),
        meta: {
          affixTab: true,
          affixTabOrder: 2,
          icon: 'mdi:file-document-multiple-outline',
          title: '项目报告生成',
          keepAlive: true,
        },
      },
    ],
  },
];

export default routes;