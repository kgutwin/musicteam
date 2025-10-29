<template>
  <div class="p-2 flex flex-row gap-2 rounded-lg bg-white">
    <div>
      <button @click="rotateType" :title="sheet.type.slice(2)">
        <Icon :name="typeIcon[sheet.type]" />
      </button>
    </div>
    <div class="grow" :class="{ 'cursor-grab': draggable }">
      {{ song?.title }} ({{ songSheet?.key }})
    </div>
    <MtDropdown>
      <div class="italic">Move to ...</div>
      <button
        v-for="position in songPositions"
        :key="position.id"
        type="button"
        @click="() => addTo(position.id)"
      >
        <Icon name="ri:music-2-line" class="mr-1" />
        {{ position.label }}
      </button>
      <button v-if="currentPositionId" @click="() => addTo(null)">
        <Icon name="ri:folder-music-line" class="mr-1" />
        Candidates
      </button>

      <hr />

      <button v-if="currentPositionId" @click="() => setType('1:primary')">
        <Icon :name="typeIcon['1:primary']" />
        Primary
      </button>
      <button v-if="currentPositionId" @click="() => setType('2:secondary')">
        <Icon :name="typeIcon['2:secondary']" />
        Secondary
      </button>
      <button v-if="currentPositionId" @click="() => setType('3:extra')">
        <Icon :name="typeIcon['3:extra']" />
        Extra
      </button>
      <button @click="() => setType('4:candidate-high')">
        <Icon :name="typeIcon['4:candidate-high']" />
        Candidate (high)
      </button>
      <button @click="() => setType('5:candidate')">
        <Icon :name="typeIcon['5:candidate']" />
        Candidate
      </button>
      <button @click="() => setType('6:candidate-low')">
        <Icon :name="typeIcon['6:candidate-low']" />
        Candidate (low)
      </button>

      <hr />

      <button class="text-red-500" @click="remove">
        <Icon name="ri:delete-bin-6-line" class="mr-1" />
        Remove
      </button>
    </MtDropdown>
  </div>
</template>

<script setup lang="ts">
import { useSongStore, useSongSheetStore } from "@/stores/songs"
import { useSetlistPositionlistStore, useSetlistRefreshStore } from "@/stores/setlists"
import { api } from "@/services"

import type { SetlistSheet } from "@/services/api"

const props = defineProps<{
  draggable?: boolean
  sheet: SetlistSheet
  currentPositionId?: string
}>()

type SetlistSheetType = SetlistSheet["type"]

const typeIcon: Record<SetlistSheetType, string> = {
  "1:primary": "ri:file-text-line",
  "2:secondary": "ri:file-copy-2-line",
  "3:extra": "ri:file-info-line",
  "4:candidate-high": "ri:star-line",
  "5:candidate": "ri:stop-large-line",
  "6:candidate-low": "ri:question-line",
}

const song = useSongStore().get({ songId: props.sheet.song_id }).data
const songSheet = useSongSheetStore().get({
  songId: props.sheet.song_id,
  versionId: props.sheet.song_version_id,
  sheetId: props.sheet.song_sheet_id,
}).data
const positionlist = useSetlistPositionlistStore().get({
  setlistId: props.sheet.setlist_id,
}).data

const songPositions = computed(() => {
  const all = positionlist.value?.positions ?? []
  return all.filter((p) => p.is_music && p.id != props.currentPositionId)
})

const refreshSetlists = useSetlistRefreshStore()

async function addTo(positionId: string | null) {
  const newType: SetlistSheetType = !positionId ? "5:candidate" : props.sheet.type

  // patch the current object
  props.sheet.setlist_position_id = positionId
  props.sheet.type = newType

  await api.setlists.updateSetlistSheet(props.sheet.setlist_id, props.sheet.id, {
    setlist_position_id: positionId,
    type: newType,
  })

  await refreshSetlists.refresh({ setlistId: props.sheet.setlist_id })
}

async function setType(type: SetlistSheetType) {
  await api.setlists.updateSetlistSheet(props.sheet.setlist_id, props.sheet.id, {
    type,
  })

  await refreshSetlists.refresh({ setlistId: props.sheet.setlist_id })
}

async function rotateType() {
  let newType = props.sheet.type
  if (props.currentPositionId) {
    // rotate between 1 -> 2 -> 3 -> 1 ...
    if (props.sheet.type === "1:primary") {
      newType = "2:secondary"
    } else if (props.sheet.type === "2:secondary") {
      newType = "3:extra"
    } else {
      newType = "1:primary"
    }
  } else {
    // rotate between 5 -> 4 -> 6 -> 5 ...
    if (props.sheet.type === "5:candidate") {
      newType = "4:candidate-high"
    } else if (props.sheet.type === "4:candidate-high") {
      newType = "6:candidate-low"
    } else {
      newType = "5:candidate"
    }
  }

  await setType(newType)
}

async function remove() {
  await api.setlists.deleteSetlistSheet(props.sheet.setlist_id, props.sheet.id)

  await refreshSetlists.refresh({ setlistId: props.sheet.setlist_id })
}
</script>

<style>
.dropdown-menu hr {
  @apply border-slate-500 m-2;
}
.dropdown-menu button {
  @apply w-full text-left pl-1 py-0.5 rounded-lg hover:bg-slate-100 hover:shadow;
}
</style>
