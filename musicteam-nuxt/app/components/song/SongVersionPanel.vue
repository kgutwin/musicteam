<template>
  <div>
    <div class="div-panel my-4">
      <div class="flex flex-row gap-4 items-baseline">
        <button
          class="btn-sheet"
          :selected="selectedSheet === '!lyrics'"
          @click="selectedSheet = '!lyrics'"
        >
          Lyrics
        </button>
        <MtText v-if="sheets?.song_sheets === undefined" loading="w-20 mx-4" />
        <button
          v-for="sheet in sheets?.song_sheets ?? []"
          :key="sheet.id"
          class="btn-sheet"
          :selected="selectedSheet === sheet"
          @click="selectedSheet = sheet"
        >
          {{ sheet.type }} ({{ sheet.key }})
        </button>

        <div class="grow"></div>

        <button class="btn-gray" @click="edit">Edit...</button>
        <button class="btn-gray" @click="addSheet">Add Sheet...</button>
        <button
          v-if="activeSetlistStore.setlist"
          :disabled="selectedSheet === '!lyrics'"
          class="btn-gray"
          @click="addToCandidates"
        >
          Add as Candidate
          <Icon
            v-if="addCandidateStatus === 'pending'"
            name="svg-spinners:3-dots-fade"
            class="ml-2"
          />
        </button>
      </div>
    </div>
    <SongTextPanel
      v-if="selectedSheet === '!lyrics'"
      :verse-order="version.verse_order"
      @copy="lyricsToClipboard"
    >
      {{ version.lyrics }}
    </SongTextPanel>
    <SongTextPanel
      v-else-if="selectedSheet.object_type === 'text/plain'"
      :verse-order="version.verse_order"
    >
      <SongText
        :song-id="version.song_id"
        :version-id="version.id"
        :sheet-id="selectedSheet.id"
      />
    </SongTextPanel>
    <object
      v-else
      :data="`/api/songs/${version.song_id}/versions/${version.id}/sheets/${selectedSheet.id}/doc`"
      class="w-full h-screen"
    ></object>
  </div>
</template>

<script setup lang="ts">
import { useModal } from "tailvue"

import type { SongVersion, SongSheet } from "@/services/api"
import { api } from "@/services"
import { useSongSheetlistStore } from "@/stores/songs"
import { useActiveSetlistStore, useSetlistSheetlistStore } from "@/stores/setlists"

import type { ToasterStatus } from "@/types/toast"

const props = defineProps<{
  version: SongVersion
}>()

const emit = defineEmits<{ selected: [SongSheet | undefined] }>()

const sheetsStore = useSongSheetlistStore()
const activeSetlistStore = useActiveSetlistStore()
const setlistSheetlistStore = useSetlistSheetlistStore()

const sheets = computed(
  () =>
    sheetsStore.get({
      songId: props.version.song_id,
      versionId: props.version.id,
    }).data.value,
)

const selectedSheet = ref<"!lyrics" | SongSheet>("!lyrics")
watchEffect(() => {
  const ss = selectedSheet.value
  if (sheets.value && ss !== "!lyrics") {
    // reset the selected sheet if it's no longer in the list of sheets
    if (!sheets.value.song_sheets.some((s) => s.id === ss.id)) {
      selectedSheet.value = "!lyrics"
    }
  }
  emit("selected", ss === "!lyrics" ? undefined : ss)
})

const { query } = useRoute()
watchEffect(() => {
  if (query.sheet && sheets.value) {
    const found = sheets.value.song_sheets.find((s) => s.id === query.sheet)
    if (found) selectedSheet.value = found
  }
})

async function addSheet() {
  await navigateTo({
    path: "/songs/new",
    query: {
      song: props.version.song_id,
      version: props.version.id,
    },
  })
}

const addCandidateStatus = ref<ToasterStatus>()

async function addToCandidates() {
  const setlist = activeSetlistStore.setlist
  if (!setlist) return

  await useToaster(
    async () => {
      if (selectedSheet.value === "!lyrics") return

      await api.setlists.newSetlistSheet(setlist.id, {
        type: "5:candidate",
        song_sheet_id: selectedSheet.value.id,
      })

      await setlistSheetlistStore.refresh({ setlistId: setlist.id })
    },
    { status: addCandidateStatus },
  )
}

function lyricsToClipboard() {
  if (props.version.lyrics) navigator.clipboard.writeText(props.version.lyrics)
}

async function editCurrentVersion() {
  const sheetId = selectedSheet.value === "!lyrics" ? "lyrics" : selectedSheet.value.id
  await navigateTo({
    path: `/songs/${props.version.song_id}/edit/${props.version.id}/${sheetId}`,
  })
}

function edit() {
  const modal = useModal()

  modal.show({
    title: "What would you like to do?",
    body:
      "If you have a new set of lyrics, a new verse order, or a new song sheet, " +
      "it's probably best to click Add a New Version. If you are correcting a " +
      "mistake, click Edit Current Version.",
    primary: {
      label: "Add a New Version",
      theme: "blue",
      action: async () =>
        await navigateTo({
          path: "/songs/new",
          query: { song: props.version.song_id },
        }),
    },
    secondary: {
      label: "Edit Current Version",
      theme: "white",
      action: editCurrentVersion,
    },
  })
}
</script>

<style>
.btn-sheet {
  @apply font-semibold rounded-lg px-4 py-1 border-2 border-transparent;
  @apply hover:border-blue-500 hover:shadow hover:bg-sky-100;
}
.btn-sheet[selected="true"] {
  @apply border-blue-300 shadow hover:border-blue-500;
}
</style>
