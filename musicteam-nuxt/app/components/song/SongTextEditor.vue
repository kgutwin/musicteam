<template>
  <div class="flex flex-col">
    <textarea v-model="textContent" class="txt-panel"></textarea>
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"

const props = defineProps<{
  songId: string
  versionId: string
  sheetId: string
}>()

const emit = defineEmits<{ hasSave: [() => Promise<Blob>] }>()

const textContent = ref<string>()

const blob = await api.songs.getSongSheetDoc(
  props.songId,
  props.versionId,
  props.sheetId,
)
textContent.value = await blob.text()

onMounted(async () => {
  emit(
    "hasSave",
    async () => new Blob([textContent.value ?? ""], { type: "text/plain" }),
  )
})
</script>
