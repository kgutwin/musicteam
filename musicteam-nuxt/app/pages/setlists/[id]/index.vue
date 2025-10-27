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

    <MtTable :columns="columns" :data="positions?.positions ?? []">
      <template #label="{ row }">
        {{ row.label }}
      </template>
      <template #presenter="{ row }">
        {{ row.presenter }}
      </template>
      <template #status="{ row }">
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
      </template>
      <template #song="{ row }"> </template>
    </MtTable>
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"
import {
  useActiveSetlistStore,
  useSetlistStore,
  useSetlistPositionlistStore,
  useSetlistRefreshStore,
} from "@/stores/setlists"

import type { TableColumn } from "@/types/mt"

const activeStore = useActiveSetlistStore()
const setlistStore = useSetlistStore()
const setlistPositionlistStore = useSetlistPositionlistStore()
const refreshStore = useSetlistRefreshStore()

const { id } = useRoute().params

const setlist = setlistStore.get({ setlistId: id as string }).data
const positions = setlistPositionlistStore.get({ setlistId: id as string }).data

const columns: TableColumn[] = [
  { name: "label", title: "Label" },
  { name: "presenter", title: "Presenter" },
  { name: "status", title: "" },
  { name: "song", title: "Song" },
]

type Status = "open" | "in-progress" | "final"
function rotateStatus(status?: Status | null): Status {
  if (status === "open") return "in-progress"
  if (status === "in-progress") return "final"
  return "open"
}

async function deleteSetlist() {
  await api.setlists.deleteSetlist(id as string)

  await refreshStore.refresh()

  await navigateTo({ path: "/setlists" })
}

function makeActive() {
  if (setlist.value) {
    activeStore.setlist = setlist.value
  }
}
</script>
