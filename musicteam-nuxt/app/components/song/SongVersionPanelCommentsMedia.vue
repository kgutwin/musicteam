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
      <div v-if="numMedia" class="bg-sky-600 text-white rounded-lg px-2">
        {{ numMedia }}
      </div>
    </template>
    <template #media>
      <SongMediaPanel :song-id="songId" :version-id="versionId" />
    </template>
  </MtCollapsingPanel>
</template>

<script setup lang="ts">
import { useSongMedialistStore } from "@/stores/songs"

const props = defineProps<{ songId: string; versionId: string }>()

const mediaStore = useSongMedialistStore()

const numMedia = computed(
  () =>
    mediaStore.get({ songId: props.songId, versionId: props.versionId }).data?.value
      ?.song_media?.length,
)
</script>
