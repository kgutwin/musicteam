<template>
  <div
    v-if="active.setlist"
    class="bg-sky-100 p-4 shadow-xl"
    :class="{ 'w-80': panelOpen, 'w-12 relative': !panelOpen }"
  >
    <button
      class="float-right mt-2 transition-transform"
      :class="{ 'rotate-90': !panelOpen }"
      @click="panelOpen = !panelOpen"
    >
      <Icon name="ri:menu-line" size="20" />
    </button>

    <div v-if="panelOpen">
      <h1>Active Set List:</h1>
      <h2>
        <NuxtLink :to="`/setlists/${active.setlist.id}`" class="hover:underline">
          {{ active.setlist.service_date }} - {{ active.setlist.leader_name }}
        </NuxtLink>
      </h2>

      <hr />

      <div class="italic">Candidates</div>

      <div class="rounded-lg bg-white min-h-20">
        <SetlistSidebarSong
          v-for="sheet in filtered(slist?.sheets)"
          :key="sheet.id"
          :sheet="sheet"
        >
        </SetlistSidebarSong>
      </div>

      <div class="mt-4">
        <div v-for="position in plist?.positions ?? []" :key="position.id">
          <ul class="flex flex-row list-disc ml-4">
            <li :class="{ 'font-bold': position.is_music }">
              {{ position.label }}
            </li>
            <hr class="grow" />
          </ul>
          <div v-if="position.is_music" class="rounded-lg bg-white min-h-8 mb-1">
            <SetlistSidebarSong
              v-for="sheet in filtered(slist?.sheets, position.id)"
              :key="sheet.id"
              :sheet="sheet"
              :current-position-id="position.id"
            />
          </div>
        </div>
      </div>

      <div class="mt-12">
        <button class="btn-gray" @click="active.setlist = null">Make Inactive</button>
      </div>
    </div>
    <div v-else class="absolute rotate-90 top-40 -right-14 w-40">
      Set List: <span class="font-bold">{{ active.setlist.service_date }}</span>
    </div>
  </div>
  <div v-else />
</template>

<script setup lang="ts">
import {
  useActiveSetlistStore,
  useSetlistPositionlistStore,
  useSetlistSheetlistStore,
} from "@/stores/setlists"

import type { SetlistSheet } from "@/services/api"

const active = useActiveSetlistStore()
const positionlist = useSetlistPositionlistStore()
const sheetlist = useSetlistSheetlistStore()

const panelOpen = ref(true)

const plist = computed(() => {
  if (!active.setlist) return undefined

  return positionlist.get({ setlistId: active.setlist.id }).data.value
})

const slist = computed(() => {
  if (!active.setlist) return undefined

  return sheetlist.get({ setlistId: active.setlist.id }).data.value
})

function filtered(sheets?: SetlistSheet[], positionId?: string): SetlistSheet[] {
  if (!sheets) return []
  return sheets.filter((s) => s.setlist_position_id == positionId)
}
</script>
