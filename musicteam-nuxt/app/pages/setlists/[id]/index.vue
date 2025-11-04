<template>
  <div>
    <Head>
      <Title>{{ setlist?.service_date }} Set List - MusicTeam</Title>
    </Head>
    <div class="div-panel">
      <div class="flex flex-row gap-2">
        <h1 class="grow">
          Set List for
          <MtEditable
            :model="setlist"
            prop="service_date"
            type="date"
            @save="saveSetlist('service_date')"
          />
        </h1>
        <button class="btn-red" @click="deleteSetlist">Delete</button>
        <button class="btn-gray" @click="editOrder = !editOrder">
          {{ editOrder ? "Done Editing Order" : "Edit Order" }}
        </button>
        <button class="btn-gray" @click="makeActive">Make Active</button>
      </div>
      <div class="flex flex-row">
        <h2 class="grow">
          Leader:
          <MtEditable
            :model="setlist"
            prop="leader_name"
            @save="saveSetlist('leader_name')"
          />
        </h2>
        <div>
          <span v-for="tag in setlist?.tags ?? []" :key="tag" class="spn-tag">
            {{ tag }}
          </span>
        </div>
      </div>
    </div>

    <MtTable :columns="columns" :data="positions?.positions" @drag-end="dragPosition">
      <template #label="{ row }">
        <span :class="{ italic: !row.is_music }">
          <MtEditable :model="row" prop="label" @save="savePosition(row, 'label')" />
        </span>
      </template>
      <template #presenter="{ row }">
        <MtEditable
          :model="row"
          prop="presenter"
          @save="savePosition(row, 'presenter')"
        />
      </template>
      <template #is-music="{ row }">
        <input
          type="checkbox"
          v-model="row.is_music"
          @change="savePosition(row, 'is_music')"
        />
      </template>
      <template #song="{ row }">
        <template v-if="row.is_music">
          <SetlistSidebarSong
            v-for="sheet in filtered(slist?.sheets, row.id)"
            :key="sheet.id"
            :sheet="sheet"
            :current-position-id="row.id"
          />
        </template>
      </template>
      <template #controls="{ row }">
        <div class="flex flex-row gap-1">
          <button @click="addPosition(row)">
            <Icon name="ri:add-large-line" size="20" />
          </button>
          <button class="hover:text-red-500" @click="deletePosition(row)">
            <Icon name="ri:delete-bin-6-line" size="20" />
          </button>
          <button class="drag-handle"><Icon name="ri:draggable" size="20" /></button>
        </div>
      </template>
    </MtTable>

    <div class="mt-8 rounded-lg shadow-lg grid grid-cols-2 gap-2">
      <div class="italic col-span-2 p-2 bg-gray-200">Candidates</div>
      <SetlistSidebarSong
        v-for="sheet in filtered(slist?.sheets)"
        :key="sheet.id"
        :sheet="sheet"
      />
      <div
        v-if="filtered(slist?.sheets).length === 0"
        class="col-span-2 italic p-2 text-center"
      >
        <div class="font-bold">No candidates added</div>
        <div v-if="!activeStore.setlist" class="text-gray-600">
          Make the set list Active using the button above to be able to add songs as
          candidates
        </div>
      </div>
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

import type { SetlistSheet, SetlistPosition, Setlist } from "@/services/api"
import type { TableColumn } from "@/types/mt"
import type { SortableEvent } from "vue-draggable-next"

const activeStore = useActiveSetlistStore()
const setlistStore = useSetlistStore()
const setlistPositionlistStore = useSetlistPositionlistStore()
const sheetlistStore = useSetlistSheetlistStore()
const refreshStore = useSetlistRefreshStore()

const { id } = useRoute().params

const setlist = setlistStore.get({ setlistId: id as string }).data
const positions = setlistPositionlistStore.get({ setlistId: id as string }).data
const slist = sheetlistStore.get({ setlistId: id as string }).data

const editOrder = ref(false)

const columns = computed(() => {
  const rv: TableColumn[] = [
    { name: "label", title: "Label" },
    { name: "presenter", title: "Presenter" },
    { name: "song", title: "Song" },
  ]
  if (editOrder.value) {
    rv.splice(2, 0, { name: "is-music", title: "Is Music?" })
    rv.push({ name: "controls", title: "", cls: "w-24" })
  }
  return rv
})

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

async function saveSetlist(field: keyof Setlist) {
  if (!setlist.value) return
  await api.setlists.updateSetlist(id as string, { [field]: setlist.value[field] })
  await refreshStore.refresh({ setlistId: id as string })
}

async function savePosition(position: SetlistPosition, field: keyof SetlistPosition) {
  await api.setlists.updateSetlistPosition(id as string, position.id, {
    [field]: position[field],
  })
  if (field === "is_music" && !position[field]) {
    for (const sheet of slist.value?.sheets ?? []) {
      if (sheet.setlist_position_id === position.id) {
        await api.setlists.updateSetlistSheet(id as string, sheet.id, {
          setlist_position_id: null,
        })
      }
    }
  }
  await refreshStore.refresh({ setlistId: id as string })
}

async function addPosition(position: SetlistPosition) {
  // what we really need to do is update the index of every position after this
  // one, then add a new position
  if (!positions.value) return
  const promises = []
  for (let i = positions.value.positions.length - 1; i >= 0; i--) {
    const pos = positions.value.positions[i]
    if (!pos || pos.id === position.id) break
    promises.push(
      api.setlists.updateSetlistPosition(id as string, pos.id, {
        index: pos.index + 1,
      }),
    )
  }
  await Promise.all(promises)

  await api.setlists.newSetlistPosition(id as string, {
    index: position.index + 1,
    label: "",
    is_music: true,
  })
  await refreshStore.refresh({ setlistId: id as string })
}

async function dragPosition(event: SortableEvent) {
  if (event.newIndex === event.oldIndex) return
  if (event.newIndex === undefined || event.oldIndex === undefined) return
  if (!positions.value) return

  const positionIds = positions.value.positions.map((p) => p.id)
  const movingId = positionIds.splice(event.oldIndex, 1)[0]
  if (movingId === undefined) return
  positionIds.splice(event.newIndex, 0, movingId)

  const promises = []
  for (let i = 0; i < positionIds.length; i++) {
    promises.push(
      api.setlists.updateSetlistPosition(id as string, positionIds[i]!, {
        index: i + 1,
      }),
    )
  }
  await Promise.all(promises)

  await refreshStore.refresh({ setlistId: id as string })
}

async function deletePosition(position: SetlistPosition) {
  await api.setlists.deleteSetlistPosition(id as string, position.id)
  await refreshStore.refresh({ setlistId: id as string })
}
</script>
