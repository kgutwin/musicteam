<template>
  <div class="song-text-panel">
    <div class="sm:float-right sm:text-right">
      <slot name="copy" />
      <div v-if="verseOrder" class="panel-verse-order">
        Order:
        {{ verseOrder.replace(/\s+/g, "\n") }}
      </div>
    </div>
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  verseOrder?: string | null
}>()
</script>

<style>
.song-text-panel {
  @apply whitespace-pre-wrap font-mono text-sm sm:text-base xl:mx-24 2xl:mx-48;
  @apply border shadow-lg p-4 sm:p-8;

  & .panel-verse-order {
    @apply p-4 mb-4 bg-slate-100 shadow font-bold;
    @apply max-sm:whitespace-normal;
  }
}
</style>
