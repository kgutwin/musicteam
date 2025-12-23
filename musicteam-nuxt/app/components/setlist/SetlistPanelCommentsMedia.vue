<template>
  <MtCollapsingPanel :cols="['comments', 'media']">
    <template #comments-head>
      <label>Comments</label>
      <CommentsIcons :resource-id="setlistId" class="h-6" />
    </template>
    <template #comments>
      <CommentsPanel class="mt-1" :resource-id="setlistId" />
    </template>

    <template #media-head>
      <label>Media</label>
      <div v-if="numMedia" class="bg-sky-600 text-white rounded-lg px-2">
        {{ numMedia }}
      </div>
    </template>
    <template #media>
      <SetlistMediaPanel :setlist-id="setlistId" />
    </template>
  </MtCollapsingPanel>
</template>

<script setup lang="ts">
import { useSongMedialistStore } from "@/stores/songs"
import { useSetlistSheetlistStore } from "@/stores/setlists"

const props = defineProps<{ setlistId: string }>()

const songMediaStore = useSongMedialistStore()
const sheetlistStore = useSetlistSheetlistStore()

const numMedia = computed(() => {
  let rv: Record<string, number> = {}
  const sheets = sheetlistStore.get({ setlistId: props.setlistId }).data
  for (const sheet of sheets.value?.sheets ?? []) {
    rv[sheet.song_version_id] =
      songMediaStore.get({
        songId: sheet.song_id,
        versionId: sheet.song_version_id,
      }).data?.value?.song_media?.length ?? 0
  }
  return Object.values(rv).reduce((acc, v) => acc + v, 0)
})
</script>
