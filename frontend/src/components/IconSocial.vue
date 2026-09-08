<!--
  社交图标（内联本地 SVG）
  用法：<IconSocial name="qq|wechat|github|mail" />
  图标源为本地打包的 assets/icons/*.svg，随组件打包，无运行时外链。
-->
<template>
  <span class="icon-social" :aria-label="name" v-html="svg" />
</template>

<script setup>
import qq from '../assets/icons/qq.svg?raw'
import wechat from '../assets/icons/wechat.svg?raw'
import github from '../assets/icons/github.svg?raw'
import mail from '../assets/icons/mail.svg?raw'

const props = defineProps({
  name: { type: String, required: true },
})

const ICONS = { qq, wechat, github, mail }
const svg = ICONS[props.name] || ''
</script>

<style scoped>
.icon-social {
  display: inline-flex;
  line-height: 1;
}
.icon-social :deep(svg) {
  width: 1.15em;
  height: 1.15em;
  display: block;
  fill: currentColor;
}
</style>
