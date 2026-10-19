<template>
  <MtCollapsingTabPanel :cols="['previous', 'similar']">
    <template #previous-head>
      <label>Previous Set Lists</label>
    </template>
    <template #previous>
      <div class="similar-bin">
        <div
          v-for="setlist in historySetlists?.setlists ?? []"
          :key="setlist.id"
          class="similar-card"
        >
          <NuxtLink :to="`/setlists/${setlist.id}`">
            <div class="flex flex-row items-baseline">
              <h2 class="grow">{{ localdate(setlist.service_date) }}</h2>
              <h3>{{ setlist.leader_name }}</h3>
            </div>
          </NuxtLink>
          <div class="mt-1 flex flex-col gap-1">
            <SetlistSidebarSong
              v-for="sheet in setlistSheets(setlist.id, setlist.sheet_ids)"
              :sheet="sheet"
              :key="sheet.id"
              read-only
            />
          </div>
        </div>
        <div v-if="historySetlists?.setlists?.length === 0">
          <i>This song has not yet appeared in any previous set lists...</i>
        </div>
      </div>
    </template>

    <template #similar-head>
      <label>Similar Songs</label>
    </template>
    <template #similar>
      <div class="similar-bin">
        <div
          v-for="songVersion in similar?.song_versions ?? []"
          :key="songVersion.id"
          class="similar-card"
        >
          <NuxtLink :to="`/songs/${songVersion.song_id}?version=${songVersion.id}`">
            <div class="flex flex-row items-baseline">
              <h2 class="grow">
                <MtText
                  :text="songs.get({ songId: songVersion.song_id }).data.value?.title"
                />
              </h2>
              <h3>{{ songVersion.label }}</h3>
            </div>
          </NuxtLink>
          <div
            class="whitespace-pre max-h-72 mt-2"
            :class="{ 'overflow-x-hidden overflow-y-auto': showMore[songVersion.id] }"
          >
            {{ trimTitle(songVersion.lyrics ?? "", showMore[songVersion.id]) }}
          </div>
          <button
            v-if="!showMore[songVersion.id]"
            class="text-blue-500 italic"
            @click="showMore[songVersion.id] = true"
          >
            show more...
          </button>
        </div>
      </div>
    </template>
  </MtCollapsingTabPanel>
</template>

<script setup lang="ts">
import { useSetlistSheetStore } from "@/stores/setlists"
import { useSongHistorySetlistsStore } from "@/stores/history"
import { useSongStore, useSongVersionSimilarlistStore } from "@/stores/songs"
import { localdate } from "@/utils"

const props = defineProps<{
  id: string
  versionId: string
}>()

const songs = useSongStore()
const ss = useSetlistSheetStore()
const historySetlists = useSongHistorySetlistsStore().get({ songId: props.id }).data
const similar = computed(
  () =>
    useSongVersionSimilarlistStore().get({
      songId: props.id,
      versionId: props.versionId,
    }).data.value,
)

function setlistSheets(setlistId: string, sheetIds: string[]) {
  const rv = []
  for (const sheetId of sheetIds) {
    const sheet = ss.get({ setlistId, sheetId }).data.value
    if (sheet) rv.push(sheet)
  }
  return rv
}

const showMore = ref<Record<string, boolean>>({})

function trimTitle(lyrics: string, showAll?: boolean) {
  lyrics = lyrics.replace(/^.*\n/, "").trim()
  return showAll ? lyrics : lyrics.split("\n").slice(0, 13).join("\n")
}
</script>

<style>
.similar-bin {
  @apply bg-white shadow-inner p-2 mt-4 flex flex-row gap-2 overflow-auto;
}
.similar-card {
  @apply w-80 shrink-0 bg-slate-100 p-2 shadow-md text-sm;

  & h2 {
    @apply text-sm;
  }
  & h3 {
    @apply text-xs;
  }
}
</style>
