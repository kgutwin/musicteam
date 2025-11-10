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

    <MtTabPanel v-model="selectedTab" :options="tabs">
      <template v-if="selectedTab === 'order'">
        <button class="btn-gray" @click="editOrder = !editOrder">
          {{ editOrder ? "Done" : "Edit" }}
        </button>
        <button class="btn-gray" @click="makeActive">Make Active</button>
      </template>
      <template v-else>
        <MtDropdown
          v-if="packetWarnings.length > 0"
          class="self-center"
          title="Warnings"
        >
          <template #dropdown-button>
            <Icon name="ri:error-warning-line" size="28" />
          </template>
          <span class="italic">Warnings:</span>
          <ul>
            <li v-for="warning in packetWarnings" :key="warning">{{ warning }}</li>
          </ul>
        </MtDropdown>
        <button
          v-if="selectedTab === 'pdf' || selectedTab === 'lyrics'"
          class="self-center mr-4"
          title="Download"
          @click="downloadPacket(selectedTab)"
        >
          <Icon name="solar:download-minimalistic-bold" size="28" />
        </button>
      </template>
    </MtTabPanel>

    <SetlistOrder
      v-if="selectedTab === 'order'"
      :edit-order="editOrder"
      :setlist-id="id as string"
    />
    <template v-else-if="selectedTab === 'pdf'">
      <div v-if="pdfLoading">
        Loading
        <Icon name="svg-spinners:3-dots-fade" />
      </div>
      <iframe
        :src="`/api/setlists/${id}/packet/pdf`"
        class="w-full h-screen"
        @load="pdfLoading = false"
      ></iframe>
    </template>
    <SongTextPanel v-else-if="selectedTab === 'lyrics'" @click="copyLyricsToClipboard">
      <object :data="`/api/setlists/${id}/packet/lyrics`" class="w-full h-screen" />
    </SongTextPanel>
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"
import {
  useActiveSetlistStore,
  useSetlistStore,
  useSetlistRefreshStore,
} from "@/stores/setlists"
import { useSongStore } from "@/stores/songs"

import type { SetlistSheet, SetlistPosition, Setlist } from "@/services/api"
import type { Tab } from "@/types/mt"

const activeStore = useActiveSetlistStore()
const setlistStore = useSetlistStore()
const setlistPositionlistStore = useSetlistPositionlistStore()
const sheetlistStore = useSetlistSheetlistStore()
const refreshStore = useSetlistRefreshStore()
const songStore = useSongStore()

const { id } = useRoute().params

const setlist = setlistStore.get({ setlistId: id as string }).data
const positions = setlistPositionlistStore.get({ setlistId: id as string }).data
const slist = sheetlistStore.get({ setlistId: id as string }).data

const tabs: Tab[] = [
  { name: "order", title: "Set List Order" },
  { name: "pdf", title: "Music Packet" },
  { name: "lyrics", title: "Lyrics Packet" },
]
const selectedTab = ref("order")

const editOrder = ref(false)

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

async function saveSetlist(field: keyof Setlist) {
  if (!setlist.value) return
  await api.setlists.updateSetlist(id as string, { [field]: setlist.value[field] })
  await refreshStore.refresh({ setlistId: id as string })
}

const pdfLoading = ref(false)
watchEffect(() => {
  if (selectedTab.value === "pdf") pdfLoading.value = true
})

const packetWarnings = computed<string[]>(() => {
  const rv: string[] = []
  if (!positions.value || !slist.value) return rv
  for (const pos of positions.value.positions) {
    if (!pos.is_music) continue
    const sheets = slist.value.sheets.filter((s) => s.setlist_position_id === pos.id)
    if (sheets.length === 0) {
      rv.push(`${pos.label} is missing a song`)
    } else if (sheets.every((s) => s.type.includes("candidate"))) {
      rv.push(`${pos.label} needs a primary song`)
    }
  }
  return rv
})

function downloadPacket(type: "pdf" | "lyrics") {
  if (!setlist.value) return
  const ext = type === "lyrics" ? "txt" : "pdf"
  const filename = `setlist-${setlist.value.service_date}.${ext}`
  const link = document.createElement("a")
  link.href = `/api/setlists/${id}/packet/${type}`
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

async function copyLyricsToClipboard() {
  const blob = await api.setlists.getSetlistPacketLyrics(id as string)
  const lyrics = await blob.text()
  console.log(lyrics)
  await navigator.clipboard.writeText(lyrics)
}
</script>
