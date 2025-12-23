<template>
  <div class="text-sm mt-1">
    <div v-for="sheet in sheets">
      <h3>{{ songStore.get({ songId: sheet.song_id }).data.value?.title }}</h3>
      <template v-for="entry in sheet.media">
        <MediaEntry
          :media="entry"
          :song-id="sheet.song_id"
          :version-id="entry.song_version_id"
        />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useSongStore, useSongMedialistStore } from "@/stores/songs"
import {
  useSetlistSheetlistStore,
  useSetlistPositionlistStore,
} from "@/stores/setlists"

import type { Song, SongMedia, SetlistSheet } from "@/services/api"

const props = defineProps<{ setlistId: string }>()

const songStore = useSongStore()
const songMediaStore = useSongMedialistStore()
const sheetlistStore = useSetlistSheetlistStore()
const positionlistStore = useSetlistPositionlistStore()

const positions = positionlistStore.get({ setlistId: props.setlistId }).data

function byPositionIndex(a: SetlistSheet, b: SetlistSheet) {
  const pos = positions.value?.positions ?? []
  const aIdx = pos.find((p) => p.id === a.setlist_position_id)?.index ?? -1
  const bIdx = pos.find((p) => p.id === b.setlist_position_id)?.index ?? -1
  return aIdx - bIdx
}

type AnnotatedSetlistSheet = SetlistSheet & { media: SongMedia[] }

const sheets = computed<AnnotatedSetlistSheet[]>(() => {
  const rv: Record<string, AnnotatedSetlistSheet> = {}
  const sheets = sheetlistStore.get({ setlistId: props.setlistId }).data
  for (const sheet of sheets.value?.sheets ?? []) {
    const song_media =
      songMediaStore.get({ songId: sheet.song_id, versionId: sheet.song_version_id })
        .data?.value?.song_media ?? []
    if (song_media.length > 0 && sheet.setlist_position_id) {
      rv[sheet.song_id] = { ...sheet, media: song_media }
    }
  }
  return Object.values(rv).toSorted(byPositionIndex)
})
</script>
