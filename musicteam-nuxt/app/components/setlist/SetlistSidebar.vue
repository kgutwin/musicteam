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

      <div class="italic flex flex-row">
        <div class="grow">Candidates</div>
        <div>
          <NuxtLink to="/songs" class="text-blue-500 hover:underline">
            Find songs
          </NuxtLink>
        </div>
      </div>

      <div class="rounded-lg bg-white">
        <draggable
          :model-value="filtered(slist?.sheets)"
          class="min-h-20"
          group="songs"
          @change="(ev) => draggableChange(ev, null)"
        >
          <SetlistSidebarSong
            v-for="sheet in filtered(slist?.sheets)"
            :draggable="true"
            :key="sheet.id"
            :sheet="sheet"
          />
        </draggable>
      </div>

      <div class="mt-4">
        <div v-for="position in plist?.positions ?? []" :key="position.id">
          <ul class="flex flex-row list-disc ml-4">
            <li :class="{ 'font-bold': position.is_music }">
              {{ position.label }}
            </li>
            <hr class="grow" />
          </ul>
          <div v-if="position.is_music" class="rounded-lg bg-white mb-1">
            <draggable
              :model-value="filtered(slist?.sheets, position.id)"
              class="min-h-8"
              group="songs"
              @change="(ev) => draggableChange(ev, position.id)"
            >
              <SetlistSidebarSong
                v-for="sheet in filtered(slist?.sheets, position.id)"
                :key="sheet.id"
                :draggable="true"
                :sheet="sheet"
                :current-position-id="position.id"
              />
            </draggable>
          </div>
        </div>
      </div>

      <div class="mt-12 flex flex-row-reverse">
        <button class="btn-gray" @click="active.setlist = null">Close</button>
      </div>
    </div>
    <div v-else class="absolute rotate-90 top-40 -right-14 w-40">
      Set List: <span class="font-bold">{{ active.setlist.service_date }}</span>
    </div>
  </div>
  <div v-else />
</template>

<script setup lang="ts">
import { VueDraggableNext as draggable } from "vue-draggable-next"

import { api } from "@/services"
import {
  useActiveSetlistStore,
  useSetlistPositionlistStore,
  useSetlistSheetlistStore,
  useSetlistRefreshStore,
} from "@/stores/setlists"

import type { SetlistSheet } from "@/services/api"
type SetlistSheetType = SetlistSheet["type"]

const active = useActiveSetlistStore()
const positionlist = useSetlistPositionlistStore()
const sheetlist = useSetlistSheetlistStore()
const refreshSetlists = useSetlistRefreshStore()

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

async function addSheetTo(sheet: SetlistSheet, positionId: string | null) {
  const newType: SetlistSheetType = !positionId ? "5:candidate" : sheet.type

  // patch the current object
  sheet.setlist_position_id = positionId
  sheet.type = newType

  await api.setlists.updateSetlistSheet(sheet.setlist_id, sheet.id, {
    setlist_position_id: positionId,
    type: newType,
  })

  await refreshSetlists.refresh({ setlistId: sheet.setlist_id })
}

async function draggableChange(
  event: { added?: { element: SetlistSheet } },
  positionId: string | null,
) {
  if (event.added) {
    await addSheetTo(event.added.element, positionId)
  }
}
</script>
