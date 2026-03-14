<template>
  <div class="div-panel div-tab-panel my-4">
    <div class="div-tab-panel-tabs">
      <button
        v-for="opt in options"
        :key="opt.name"
        class="btn-tab"
        :selected="selected === opt.name"
        @click="selected = opt.name"
      >
        <slot name="tab-button" :opt="opt">
          {{ opt.title }}
        </slot>
      </button>
      <MtText v-if="loading" loading="w-20 mx-4 self-center" />
    </div>
    <div class="div-tab-panel-buttons">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts" generic="T extends Tab">
import type { Tab } from "@/types/mt"

defineProps<{
  options: T[]
  loading?: boolean
}>()

const selected = defineModel<string>()
</script>

<style>
.div-tab-panel {
  @apply flex flex-col md:flex-row gap-x-4 gap-y-2;
}
.div-tab-panel-buttons {
  @apply flex flex-row gap-x-4 gap-y-2 items-start flex-wrap sm:flex-nowrap ml-4;
}
.div-tab-panel-tabs {
  @apply grow flex flex-row flex-wrap gap-x-2 gap-y-2;
}
.btn-tab {
  @apply font-semibold rounded-lg px-4 py-1 border-2 border-transparent;
  @apply hover:border-blue-500 hover:shadow hover:bg-sky-100;
}
.btn-tab[selected="true"] {
  @apply border-blue-300 shadow hover:border-blue-500;
}
</style>
