import type { RouteRecordRaw } from 'vue-router';

import {
  VBEN_SUBJECT_MANAGEMENT_URL,
  VBEN_GITHUB_URL,
  VBEN_PROJECT_MANAGEMENT_URL,
} from '@vben/constants';

import { IFrameView } from '#/layouts';
import { $t } from '#/locales';

const routes: RouteRecordRaw[] = [
  {
    meta: {
      badgeType: 'dot',
      icon: 'mdi:cube-outline',
      order: 9998,
      title: $t('demos.vben.title'),
    },
    name: 'VbenProject',
    path: '/vben-admin',
    children: [
      {
        name: 'VbenDocument',
        path: '/vben-admin/document',
        component: () => import('#/views/vben/document/index.vue'),
        meta: {
          icon: 'lucide:book-open-text',
          title: $t('demos.vben.document'),
        },
      },
      {
        name: 'VbenLocalProjects',
        path: '/vben-admin/projects',
        component: () => import('#/views/vben/projects/index.vue'),
        meta: {
          icon: 'lucide:folder',
          title: '本地项目',
        },
      },
      {
        name: 'VbenGithub',
        path: '/vben-admin/github',
        component: IFrameView,
        meta: {
          icon: 'mdi:github',
          link: VBEN_GITHUB_URL,
          title: 'Github',
        },
      },
      {
        name: 'VbenNaive',
        path: '/vben-admin/naive',
        component: IFrameView,
        meta: {
          badgeType: 'dot',
          icon: 'logos:naiveui',
          link: VBEN_PROJECT_MANAGEMENT_URL,
          title: '项目管理系统',
        },
      },
      {
        name: 'VbenElementPlus',
        path: '/vben-admin/ele',
        component: IFrameView,
        meta: {
          badgeType: 'dot',
          icon: 'logos:element',
          link: VBEN_SUBJECT_MANAGEMENT_URL,
          title: '受试品管理系统',
        },
      },
    ],
  },
  {
    name: 'VbenAbout',
    path: '/vben-admin/about',
    component: () => import('#/views/_core/about/index.vue'),
    meta: {
      icon: 'lucide:copyright',
      title: $t('demos.vben.about'),
      order: 9999,
    },
  },
];

export default routes;
