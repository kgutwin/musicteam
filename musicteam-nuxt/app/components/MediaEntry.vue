<template>
  <div>
    <div
      v-if="media.url"
      :href="media.url"
      class="flex flex-row sm:flex-col lg:flex-row"
    >
      <div class="basis-1/2 mr-2">{{ media.title }}</div>
      <div class="truncate">
        <a :href="media.url" class="a-hov text-gray-600" target="_blank">
          {{ media.url }}
        </a>
      </div>
      <Icon class="shrink-0 sm:hidden lg:inline" name="solar:square-top-down-outline" />
    </div>
    <div v-else-if="media.media_type">
      <div class="flex flex-row gap-2">
        <div>{{ media.title }}</div>
        <button class="text-lg" data-cy="download-media" @click="download(media)">
          <Icon name="solar:download-minimalistic-bold" />
        </button>
        <div class="italic">{{ media.media_type }}</div>
      </div>
      <audio
        v-if="mimeCategory(media.media_type) === 'audio'"
        :src="`/api/songs/${songId}/versions/${versionId}/media/${media.id}/obj`"
        controls
        class="w-full"
      />
      <video
        v-else-if="mimeCategory(media.media_type) === 'video'"
        :src="`/api/songs/${songId}/versions/${versionId}/media/${media.id}/obj`"
        controls
        class="w-full"
      />
    </div>
    <div v-if="(media.tags?.length ?? 0) > 0">
      <span v-for="tag in media.tags" :key="tag" class="spn-tag">
        {{ tag }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useSongStore } from "@/stores/songs"
import mime from "mime-types"

import type { SongMedia } from "@/services/api"

const props = defineProps<{
  media: SongMedia
  songId?: string
  versionId?: string
}>()
defineEmits<{ delete: [] }>()

const songStore = useSongStore()

async function download(media: SongMedia) {
  if (!media.media_type) return
  if (!props.songId) return

  const song = await songStore.get({ songId: props.songId }).get()
  let ext = mime.extension(media.media_type)
  if (ext === "mpga") {
    ext = "mp3" // assume mp3 is the most common
  }

  const link = document.createElement("a")

  link.href = `/api/songs/${props.songId}/versions/${props.versionId}/media/${media.id}/obj`
  link.download = `${song.title} - ${media.title}.${ext}`

  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

function mimeCategory(mimeType: string) {
  const [first] = mimeType.split("/", 1)
  return first
}
</script>
