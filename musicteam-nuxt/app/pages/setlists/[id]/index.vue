<template>
  <div>
    <div class="div-panel">
      <div class="flex flex-row gap-2">
        <h1 class="grow">Set List for {{ setlist?.service_date }}</h1>
        <button class="btn-red" @click="deleteSetlist">Delete</button>
        <button class="btn-gray" @click="makeActive">Make Active</button>
      </div>
      <div class="flex flex-row">
        <h2 class="grow">Leader: {{ setlist?.leader_name }}</h2>
        <div>
          <span v-for="tag in setlist?.tags ?? []" :key="tag" class="spn-tag">
            {{ tag }}
          </span>
        </div>
      </div>
    </div>

    <MtTable :columns="columns" :data="positions?.positions">
      <template #label="{ row }">
        {{ row.label }}
      </template>
      <template #presenter="{ row }">
        {{ row.presenter }}
      </template>
      <!-- <template #status="{ row }">
        <button
          @click="row.status = rotateStatus(row.status)"
          :title="row.status ?? ''"
        >
          <Icon
            v-if="row.is_music"
            size="20"
            :name="
              {
                open: 'tabler:circle',
                'in-progress': 'tabler:circle-half-2',
                final: 'tabler:circle-dot-filled',
              }[row.status as Status] ?? 'tabler:circle-dotted'
            "
          />
        </button>
      </template> -->
      <template #song="{ row }">
        <SetlistSidebarSong
          v-for="sheet in filtered(slist?.sheets, row.id)"
          :key="sheet.id"
          :sheet="sheet"
          :current-position-id="row.id"
        />
      </template>
    </MtTable>

    <div class="mt-8 rounded-lg shadow-lg grid grid-cols-2 gap-2">
      <div class="italic col-span-2 p-2 bg-gray-200">Candidates</div>
      <SetlistSidebarSong
        v-for="sheet in filtered(slist?.sheets)"
        :key="sheet.id"
        :sheet="sheet"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"
import {
  useActiveSetlistStore,
  useSetlistStore,
  useSetlistPositionlistStore,
  useSetlistSheetlistStore,
  useSetlistRefreshStore,
} from "@/stores/setlists"

import type { SetlistSheet } from "@/services/api"
import type { TableColumn } from "@/types/mt"

const activeStore = useActiveSetlistStore()
const setlistStore = useSetlistStore()
const setlistPositionlistStore = useSetlistPositionlistStore()
const sheetlistStore = useSetlistSheetlistStore()
const refreshStore = useSetlistRefreshStore()

const { id } = useRoute().params

const setlist = setlistStore.get({ setlistId: id as string }).data
const positions = setlistPositionlistStore.get({ setlistId: id as string }).data
const slist = sheetlistStore.get({ setlistId: id as string }).data

const columns: TableColumn[] = [
  { name: "label", title: "Label" },
  { name: "presenter", title: "Presenter" },
  // { name: "status", title: "" },
  { name: "song", title: "Song" },
]

type Status = "open" | "in-progress" | "final"
function rotateStatus(status?: Status | null): Status {
  if (status === "open") return "in-progress"
  if (status === "in-progress") return "final"
  return "open"
}

async function deleteSetlist() {
  if (!window.confirm("Are you sure you want to delete this set list?")) return

  await api.setlists.deleteSetlist(id as string)

  await refreshStore.refresh()

  await navigateTo({ path: "/setlists" })
}

function makeActive() {
  if (setlist.value) {
    activeStore.setlist = setlist.value
  }
}

function filtered(sheets?: SetlistSheet[], positionId?: string): SetlistSheet[] {
  if (!sheets) return []
  return sheets.filter((s) => s.setlist_position_id == positionId)
}
</script>
