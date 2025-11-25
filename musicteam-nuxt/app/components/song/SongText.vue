<template>
  <div>{{ songText }}</div>
</template>

<script setup lang="ts">
import { api } from "@/services"

const props = defineProps<{
  songId: string
  versionId: string
  sheetId: string
}>()

const songText = ref("")

watch(
  props,
  async () => {
    songText.value = "Loading ..."

    const blob = await api.songs.getSongSheetDoc(
      props.songId,
      props.versionId,
      props.sheetId,
    )
    songText.value = await blob.text()
  },
  { immediate: true },
)
</script>
