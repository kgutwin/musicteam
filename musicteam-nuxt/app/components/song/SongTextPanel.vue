<template>
  <div class="whitespace-pre-wrap font-mono lg:mx-48 border shadow-lg p-8">
    <div
      v-if="verseOrder"
      class="float-right p-4 bg-slate-100 shadow text-right font-bold"
    >
      Order:
      {{ verseOrder.replace(/\s+/g, "\n") }}
    </div>
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{ verseOrder: string | null | undefined }>()
</script>
