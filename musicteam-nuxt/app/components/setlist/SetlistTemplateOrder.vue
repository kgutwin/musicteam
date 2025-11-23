<template>
  <MtTable :columns="columns" :data="positions?.positions" @drag-end="dragPosition">
    <template #presenter="{ row }">
      <MtEditable
        :model="row"
        prop="presenter"
        @save="savePosition(row, 'presenter')"
        placeholder="Name"
      />
    </template>
    <template #label="{ row }">
      <span :class="{ italic: !row.is_music }">
        <MtEditable
          :model="row"
          prop="label"
          @save="savePosition(row, 'label')"
          placeholder="Label"
        />
      </span>
    </template>
    <template #is-music="{ row }">
      <input
        type="checkbox"
        v-model="row.is_music"
        @change="savePosition(row, 'is_music')"
      />
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
</template>

<script setup lang="ts">
import { api } from "@/services"
import {
  useSetlistTemplatePositionlistStore,
  useSetlistTemplateRefreshStore,
} from "@/stores/setlistTemplates"

import type { SetlistTemplate, SetlistTemplatePosition } from "@/services/api"
import type { TableColumn } from "@/types/mt"
import type { SortableEvent } from "vue-draggable-next"

const props = defineProps<{ template: SetlistTemplate }>()

const positionStore = useSetlistTemplatePositionlistStore()
const refreshStore = useSetlistTemplateRefreshStore()

const positions = positionStore.get({ templateId: props.template.id }).data

const columns: TableColumn[] = [
  { name: "presenter", title: "Presenter", cls: "w-1/3" },
  { name: "label", title: "Label", cls: "w-1/3" },
  { name: "is-music", title: "Needs Music?" },
  { name: "controls", title: "", cls: "w-24" },
]

async function savePosition(
  position: SetlistTemplatePosition,
  field: keyof SetlistTemplatePosition,
) {
  await api.setlistTemplates.updateSetlistTemplatePosition(
    props.template.id,
    position.id,
    { [field]: position[field] },
  )
  await refreshStore.refresh({ templateId: props.template.id })
}

async function addPosition(position: SetlistTemplatePosition) {
  // what we really need to do is update the index of every position after this
  // one, then add a new position
  if (!positions.value) return
  const promises = []
  for (let i = positions.value.positions.length - 1; i >= 0; i--) {
    const pos = positions.value.positions[i]
    if (!pos || pos.id === position.id) break
    promises.push(
      api.setlistTemplates.updateSetlistTemplatePosition(props.template.id, pos.id, {
        index: pos.index + 1,
      }),
    )
  }
  await Promise.all(promises)

  await api.setlistTemplates.newSetlistTemplatePosition(props.template.id, {
    index: position.index + 1,
    label: "",
    is_music: true,
  })
  await refreshStore.refresh({ templateId: props.template.id })
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
      api.setlistTemplates.updateSetlistTemplatePosition(
        props.template.id,
        positionIds[i]!,
        {
          index: i + 1,
        },
      ),
    )
  }
  await Promise.all(promises)

  await refreshStore.refresh({ templateId: props.template.id })
}

async function deletePosition(position: SetlistTemplatePosition) {
  await api.setlistTemplates.deleteSetlistTemplatePosition(
    props.template.id,
    position.id,
  )
  await refreshStore.refresh({ templateId: props.template.id })
}
</script>
