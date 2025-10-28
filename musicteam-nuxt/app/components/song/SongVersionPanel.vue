<template>
  <div>
    <div class="div-panel my-4">
      <div class="flex flex-row gap-4">
        <button
          class="btn-sheet"
          :selected="selectedSheet === '!lyrics'"
          @click="selectedSheet = '!lyrics'"
        >
          Lyrics
        </button>
        <button
          v-for="sheet in sheets?.song_sheets ?? []"
          :key="sheet.id"
          class="btn-sheet"
          :selected="selectedSheet === sheet"
          @click="selectedSheet = sheet"
        >
          {{ sheet.type }} ({{ sheet.key }})
        </button>
        <div class="grow"></div>
        <button class="btn-gray" @click="addSheet">Add Sheet...</button>
        <button
          v-if="activeSetlistStore.setlist"
          :disabled="selectedSheet === '!lyrics'"
          class="btn-gray"
          @click="addToCandidates"
        >
          Add as Candidate
        </button>
      </div>
    </div>
    <SongTextPanel
      v-if="selectedSheet === '!lyrics'"
      :verse-order="version.verse_order"
    >
      {{ version.lyrics }}
    </SongTextPanel>
    <SongTextPanel
      v-else-if="selectedSheet.object_type === 'text/plain'"
      :verse-order="version.verse_order"
    >
      <SongText
        :song-id="version.song_id"
        :version-id="version.id"
        :sheet-id="selectedSheet.id"
      />
    </SongTextPanel>
    <object
      v-else
      :data="`/api/songs/${version.song_id}/versions/${version.id}/sheets/${selectedSheet.id}/doc`"
      class="w-full h-screen"
    ></object>
  </div>
</template>

<script setup lang="ts">
import type { SongVersion, SongSheet } from "@/services/api"
import { api } from "@/services"
import { useSongSheetlistStore } from "@/stores/songs"
import { useActiveSetlistStore, useSetlistSheetlistStore } from "@/stores/setlists"

const props = defineProps<{
  version: SongVersion
}>()

const sheetsStore = useSongSheetlistStore()
const activeSetlistStore = useActiveSetlistStore()
const setlistSheetlistStore = useSetlistSheetlistStore()

const sheets = computed(
  () =>
    sheetsStore.get({
      songId: props.version.song_id,
      versionId: props.version.id,
    }).data.value,
)

const selectedSheet = ref<"!lyrics" | SongSheet>("!lyrics")

async function addSheet() {
  await navigateTo({
    path: "/songs/new",
    query: {
      song: props.version.song_id,
      version: props.version.id,
    },
  })
}

async function addToCandidates() {
  if (selectedSheet.value === "!lyrics") return
  const setlist = activeSetlistStore.setlist
  if (!setlist) return

  await api.setlists.newSetlistSheet(setlist.id, {
    type: "5:candidate",
    song_sheet_id: selectedSheet.value.id,
  })

  await setlistSheetlistStore.refresh({ setlistId: setlist.id })
}
</script>

<style>
.btn-sheet {
  @apply font-semibold rounded-lg px-4 py-1 border-2 border-transparent;
  @apply hover:border-blue-500 hover:shadow hover:bg-sky-100;
}
.btn-sheet[selected="true"] {
  @apply border-blue-300 shadow hover:border-blue-500;
}
</style>
