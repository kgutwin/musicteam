<template>
  <div>
    <h1>New Set List</h1>

    <form class="frm-edit">
      <label>
        <span>Leader's Name</span>
        <input v-model="inputLeaderName" class="inp-text" />
      </label>

      <label>
        <span>Service Date</span>
        <input v-model="inputServiceDate" type="date" class="inp-text" />
      </label>

      <label>
        <span>Tags</span>
        <MtArrayInput v-model="inputTags" allow-space />
      </label>
    </form>

    <form class="frm-edit">
      <MtTable :columns="columns" :data="positions">
        <template #label="{ row }">
          <input v-model="row.label" class="inp-text w-full" />
        </template>
        <template #presenter="{ row }">
          <input v-model="row.presenter" class="inp-text w-full" />
        </template>
        <template #is-music="{ row }">
          <input type="checkbox" v-model="row.is_music" />
        </template>
        <template #controls="{ row, index }">
          <div class="flex flex-row mt-1 gap-2">
            <button
              type="button"
              @click="
                positions.splice(index + 1, 0, { index: index + 1, is_music: true })
              "
            >
              <Icon name="lucide:plus" size="20" />
            </button>
            <button type="button" @click="positions.splice(index, 1)">
              <Icon name="lucide:trash-2" size="20" />
            </button>
          </div>
        </template>
      </MtTable>
    </form>

    <div class="flex flex-row gap-2">
      <button class="btn-gray" @click="save">Save</button>
      <button class="btn-gray" @click="cancel">Cancel</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { NewSetlistPosition } from "@/services/api"
import type { TableColumn } from "@/types/mt"

import { api } from "@/services"
import { useSetlistRefreshStore } from "@/stores/setlists"

const { data: authData } = useAuth()

const setlistRefresh = useSetlistRefreshStore()

const inputLeaderName = ref<string | undefined>(authData.value?.name)
const inputServiceDate = ref<string>("2025-11-02")
const inputTags = ref<string[]>([])

const positions = ref<Partial<NewSetlistPosition>[]>([{ index: 1, is_music: true }])
const columns: TableColumn[] = [
  { name: "label", title: "Label" },
  { name: "presenter", title: "Presenter" },
  { name: "is-music", title: "Music?" },
  { name: "controls", title: "" },
]

async function save() {
  const leaderName = inputLeaderName.value
  const serviceDate = inputServiceDate.value
  const tags = inputTags.value

  if (!leaderName) return

  const setlistResponse = await api.setlists.newSetlist({
    leader_name: leaderName,
    service_date: serviceDate,
    tags,
  })

  const setlistId = setlistResponse.data.id

  let index = 1
  for (const position of positions.value as NewSetlistPosition[]) {
    position.index = index
    await api.setlists.newSetlistPosition(setlistId, position)
    index += 1
  }

  await setlistRefresh.refresh()

  await navigateTo({ path: "/setlists" })
}

async function cancel() {
  await navigateTo({ path: "/setlists" })
}
</script>
