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
      <h2>{{ active.setlist.service_date }} - {{ active.setlist.leader_name }}</h2>

      <hr />

      <h3>Candidates</h3>

      <div class="rounded-lg bg-white h-20">
        <div v-for="sheet in slist?.sheets ?? []" :key="sheet.id">
          {{ sheet.song_sheet_id }}
        </div>
      </div>

      <h3 class="mt-8">Slots</h3>

      <div>
        <div v-for="position in plist?.positions ?? []" :key="position.id">
          {{ position.label }}
        </div>
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
</script>
