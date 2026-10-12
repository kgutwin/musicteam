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
    <template #similar> Coming soon... </template>
  </MtCollapsingTabPanel>
</template>

<script setup lang="ts">
import { useSetlistSheetStore } from "@/stores/setlists"
import { useSongHistorySetlistsStore } from "@/stores/history"
import { localdate } from "@/utils"

const props = defineProps<{ id: string }>()

const ss = useSetlistSheetStore()
const historySetlists = useSongHistorySetlistsStore().get({ songId: props.id }).data

function setlistSheets(setlistId: string, sheetIds: string[]) {
  const rv = []
  for (const sheetId of sheetIds) {
    const sheet = ss.get({ setlistId, sheetId }).data.value
    if (sheet) rv.push(sheet)
  }
  return rv
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
