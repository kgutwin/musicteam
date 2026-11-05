<template>
  <MtCollapsingPanel :cols="['comments', 'media']">
    <template #comments-head>
      <label>Comments</label>
      <CommentsIcons :resource-id="versionId" class="h-6" />
    </template>
    <template #comments>
      <CommentsPanel class="mt-1" :resource-id="versionId" />
    </template>

    <template #media-head>
      <label>Media</label>
      <MediaCount v-if="numMedia" type="media" :num="numMedia" />
      <MediaCount v-if="numRecordings" type="recording" :num="numRecordings" />
    </template>
    <template #media>
      <SongMediaPanel :song-id="songId" :version-id="versionId" />
    </template>
  </MtCollapsingPanel>
</template>

<script setup lang="ts">
import { useSongMedialistStore, useSongRecordinglistStore } from "@/stores/songs"

const props = defineProps<{ songId: string; versionId: string }>()

const mediaStore = useSongMedialistStore()
const recordingStore = useSongRecordinglistStore()

const numMedia = computed(
  () =>
    mediaStore.get({ songId: props.songId, versionId: props.versionId }).data?.value
      ?.song_media?.length,
)

const numRecordings = computed(
  () =>
    recordingStore.get({ songId: props.songId, versionId: props.versionId }).data?.value
      ?.marks?.length,
)
</script>
