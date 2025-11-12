<template>
  <div>
    <Head>
      <Title>{{ setlist?.service_date }} Set List - MusicTeam</Title>
    </Head>
    <div class="div-panel">
      <div class="flex flex-row gap-2">
        <h1 class="grow flex flex-row gap-2">
          Set List for
          <MtEditable
            :model="setlist"
            prop="service_date"
            type="date"
            @save="saveSetlist('service_date')"
          />
          <Icon name="solar:double-alt-arrow-right-bold-duotone" class="self-center" />
          <MtEditable :model="setlist" prop="title" @save="saveSetlist('title')" />
        </h1>
        <button class="btn-red" @click="deleteSetlist">Delete</button>
      </div>
      <div class="flex flex-row">
        <div class="grow">
          <h2>
            Leader:
            <MtEditable
              :model="setlist"
              prop="leader_name"
              @save="saveSetlist('leader_name')"
            />
          </h2>
          <h3>
            Participants:
            <MtEditable
              :model="setlist"
              prop="participants"
              @save="saveSetlist('participants')"
            >
              <template #input="{ modelValue, updateModelValue }">
                <MtArrayInput
                  :modelValue="modelValue"
                  @update:modelValue="updateModelValue"
                  allow-space
                />
              </template>
            </MtEditable>
          </h3>
        </div>
        <MtEditableTags :model="setlist" @save="saveSetlist('tags')" />
      </div>
    </div>

    <MtTabPanel v-model="selectedTab" :options="tabs">
      <template v-if="selectedTab === 'order'">
        <button
          class="self-center text-blue-800 hover:text-blue-600"
          title="Copy to Clipboard"
          @click="copySetlistToClipboard"
        >
          <Icon name="solar:copy-outline" size="28" />
        </button>
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
            <Icon name="solar:danger-triangle-broken" size="28" />
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
      <div v-if="pdfLoading" class="div-loading-panel">
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
import { useSongStore, useSongSheetStore } from "@/stores/songs"

import type { SetlistSheet, SetlistPosition, Setlist } from "@/services/api"
import type { Tab } from "@/types/mt"

const activeStore = useActiveSetlistStore()
const setlistStore = useSetlistStore()
const setlistPositionlistStore = useSetlistPositionlistStore()
const sheetlistStore = useSetlistSheetlistStore()
const refreshStore = useSetlistRefreshStore()
const songStore = useSongStore()
const songSheetStore = useSongSheetStore()

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

async function copySetlistToClipboard() {
  if (!positions.value || !slist.value) return
  const lines: string[] = ["Set list", "--------"]

  for (const pos of positions.value.positions) {
    if (!pos.is_music) continue
    for (const sheet of slist.value.sheets.filter(
      (s) => s.setlist_position_id === pos.id && !s.type.includes("candidate"),
    )) {
      const song = await songStore.get({ songId: sheet.song_id }).get()
      const songsheet = await songSheetStore
        .get({
          songId: sheet.song_id,
          versionId: sheet.song_version_id,
          sheetId: sheet.song_sheet_id,
        })
        .get()
      lines.push(`${pos.label}: ${song.title} (${songsheet.key}) [#${song.ccli_num}]`)
    }
  }

  navigator.clipboard.writeText(lines.join("\n"))
}

async function copyLyricsToClipboard() {
  const lyrics = new Promise<string>(async (resolve, reject) => {
    try {
      const blob = await api.setlists.getSetlistPacketLyrics(id as string)
      resolve(await blob.text())
    } catch (error) {
      reject(error)
    }
  })
  const clipboardItem = new ClipboardItem({ "text/plain": lyrics })
  await navigator.clipboard.write([clipboardItem])
}
</script>
