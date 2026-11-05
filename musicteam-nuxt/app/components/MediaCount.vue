<template>
  <div
    class="relative text-white rounded-lg mx-1 px-2"
    :class="{ 'bg-sky-600': type === 'media', 'bg-cyan-600': type === 'recording' }"
  >
    <Icon
      :name="
        type === 'recording'
          ? 'solar:record-circle-bold'
          : 'solar:chat-round-video-bold'
      "
      class="absolute -top-2 -right-2 text-gray-700"
    />
    {{ num }}
  </div>
</template>

<script setup lang="ts">
defineProps<{
  type: "media" | "recording"
  num: number
}>()
</script>
