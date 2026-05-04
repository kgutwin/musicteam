<template>
  <div class="flex flex-col">
    <textarea
      v-model="textContent"
      class="txt-panel with-size-guide"
      :class="short ? 'h-[30rem]' : 'h-[48rem]'"
      data-cy="song-text-editor"
    >
    </textarea>
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"

const props = defineProps<{
  songId?: string
  versionId?: string
  sheetId?: string
  short?: boolean
}>()

const emit = defineEmits<{ hasSave: [() => Promise<Blob>] }>()

const textContent = ref<string>()

if (props.songId && props.versionId && props.sheetId) {
  const blob = await api.songs.getSongSheetDoc(
    props.songId,
    props.versionId,
    props.sheetId,
  )
  textContent.value = await blob.text()
}

onMounted(async () => {
  emit(
    "hasSave",
    async () => new Blob([textContent.value ?? ""], { type: "text/plain" }),
  )
})
</script>

<style>
.with-size-guide {
  background-image: linear-gradient(to right, rgb(255 200 200), white);
  background-repeat: no-repeat;
  background-size: 1ch 100%;
  /* 60 chars of text plus 4ch left padding */
  background-position-x: 64ch;
}
</style>
