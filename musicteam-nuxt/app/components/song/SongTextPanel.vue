<template>
  <div
    class="whitespace-pre-wrap font-mono text-sm sm:text-base xl:mx-24 2xl:mx-48 border shadow-lg p-4 sm:p-8"
  >
    <div class="sm:float-right text-right">
      <div v-if="!noCopy" class="pr-4 pb-2">
        <button
          class="text-blue-500 hover:text-blue-700"
          @click="$emit('copy')"
          title="Copy to Clipboard"
        >
          <Icon name="solar:copy-outline" />
        </button>
      </div>
      <div v-if="verseOrder" class="p-4 mb-4 bg-slate-100 shadow font-bold">
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
  noCopy?: boolean
}>()
defineEmits<{ copy: [] }>()
</script>
