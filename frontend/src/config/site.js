/**
 * 站点集中配置 —— 以后要改站名 / 个人介绍 / 社交账号 / 备案号，只改这里即可。
 */

export const site = {
  /**
   * 站名与副标题
   * 「萤窗」取自「囊萤映雪」—— 车胤家贫，夏夜以练囊盛萤火照书苦读，
   * 故「萤窗」即借萤火读书之窗，喻勤学。与整站萤火/星空视觉一脉相承。
   */
  name: '萤窗小记',
  slogan: '写代码，也仰望星空',

  /** 头像（放在 frontend/public/ 下的静态资源） */
  avatar: '/firefly-avatar.png',

  /** 个人简介（显示在左侧栏个人卡片）—— 可自行补充学校 / 专业等更多信息 */
  intro: '北京信息科技大学·软件工程在读，主攻 Python / 数据分析 / 大模型应用开发，也写 Vue 与 Spring。在这里记录代码、学习与生活。',
  owner: {
    nickname: '萤火旅人',
    school: '北京信息科技大学 · 软件工程',
    location: '北京',
    motto: '写代码，也仰望星空。',
  },

  /**
   * 社交链接。
   *  - url   ：点击后跳转的地址（外链 / mailto）；留空表示不跳转
   *  - copy  ：点击时复制到剪贴板的账号文本（联系方式类都有，保证点了一定有反应）
   *  - toast ：点击后弹出的提示文案
   *  - title ：悬浮（自绘 tooltip）显示的账号信息
   */
  socials: [
    { name: 'QQ', icon: 'qq', url: '', copy: '2414857241', toast: '已复制 QQ 号：2414857241', title: 'QQ：2414857241' },
    { name: '微信', icon: 'wechat', url: '', copy: 'xwnkxjh_wadr', toast: '已复制微信号：xwnkxjh_wadr', title: '微信：xwnkxjh_wadr' },
    { name: 'GitHub', icon: 'github', url: 'https://github.com/YzhTravelInsights', title: 'GitHub：YzhTravelInsights' },
    { name: '邮箱', icon: 'mail', url: 'mailto:yzh0715@163.com', copy: 'yzh0715@163.com', toast: '已复制邮箱：yzh0715@163.com', title: '邮箱：yzh0715@163.com' },
  ],

  /**
   * ICP 备案。未部署时留空，footer 会显示「ICP 备案号待补充」；
   * 部署后填上备案号（如 '京ICP备00000000号-1'）即可自动展示。
   */
  icp: {
    number: '', // 例：'京ICP备00000000号-1'
    url: 'https://beian.miit.gov.cn/',
  },

  /** 侧边栏公告 */
  announcement: '欢迎来到流萤的星空 ✨ 愿这里的光，能照亮你的一小段旅程。',
}
