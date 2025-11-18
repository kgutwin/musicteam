<template>
  <div>
    <div class="div-panel div-tab-panel my-4">
      <MtText v-if="loading" loading="w-20 mx-4" />
      <button
        v-else
        v-for="opt in options"
        :key="opt.name"
        class="btn-tab"
        :selected="selected === opt.name"
        @click="selected = opt.name"
      >
        {{ opt.title }}
      </button>
      <div class="sm:grow" />
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Tab } from "@/types/mt"

defineProps<{
  options: Tab[]
  loading?: boolean
}>()

const selected = defineModel<string>()
</script>

<style>
.div-tab-panel {
  @apply flex flex-row gap-4 items-baseline flex-wrap sm:flex-nowrap;
}
.btn-tab {
  @apply font-semibold rounded-lg px-4 py-1 border-2 border-transparent;
  @apply hover:border-blue-500 hover:shadow hover:bg-sky-100;
}
.btn-tab[selected="true"] {
  @apply border-blue-300 shadow hover:border-blue-500;
}
</style>
