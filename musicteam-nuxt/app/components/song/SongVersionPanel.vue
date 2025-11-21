<template>
  <div>
    <MtTabPanel
      v-model="selected"
      :loading="sheets?.song_sheets === undefined"
      :options="sheetTabs"
    >
      <button
        class="self-end mr-4 btn-icon"
        title="Download"
        @click="download(selectedSheet)"
      >
        <Icon name="solar:download-minimalistic-bold" />
      </button>
      <button class="btn-gray" @click="edit">
        <Icon name="ri:edit-2-line" class="show-lg" />
        <span class="hide-lg">Edit...</span>
      </button>
      <button class="btn-gray" @click="addSheet">
        <Icon name="ri:add-large-line" class="show-lg" />
        <span class="hide-lg">Add Sheet...</span>
      </button>
      <button
        v-if="activeSetlistStore.setlist"
        :disabled="selectedSheet === '!lyrics'"
        class="btn-gray"
        @click="addToCandidates"
      >
        <Icon name="ri:play-list-add-line" class="show-lg" />
        <span class="hide-lg">Add as Candidate</span>
        <Icon
          v-if="addCandidateStatus === 'pending'"
          name="svg-spinners:3-dots-fade"
          class="ml-2"
        />
      </button>
    </MtTabPanel>

    <SongTextPanel
      v-if="selectedSheet === '!lyrics'"
      :verse-order="version.verse_order"
      @copy="lyricsToClipboard"
    >
      {{ version.lyrics ?? "Lyrics are missing, use the Edit button to add them!" }}
    </SongTextPanel>
    <SongTextPanel
      v-else-if="selectedSheet.object_type === 'text/plain'"
      :verse-order="selectedSheet.auto_verse_order ? version.verse_order : null"
      no-copy
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
  title: string
  version: SongVersion
}>()

const emit = defineEmits<{ selected: [SongSheet | undefined] }>()

const { query } = useRoute()

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

const sheetTabs = computed(() => {
  return [{ name: "!lyrics", title: "Lyrics" }].concat(
    (sheets.value?.song_sheets ?? []).map((s) => ({
      name: s.id,
      title: `${s.type} (${s.key})`,
    })),
  )
})
const selected = ref<string>((query.sheet as string) ?? "!lyrics")
const selectedSheet = computed<"!lyrics" | SongSheet>(
  () => sheets?.value?.song_sheets?.find((s) => s.id === selected.value) ?? "!lyrics",
)

watchEffect(() => {
  let ss = selected.value
  if (sheets.value) {
    if (ss !== "!lyrics") {
      // reset the selected sheet if it's no longer in the list of sheets
      if (!sheets.value.song_sheets.some((s) => s.id === ss)) {
        ss = selected.value = "!lyrics"
      }
    }
    emit(
      "selected",
      sheets.value.song_sheets.find((s) => s.id === ss),
    )
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
        song_sheet_id: selected.value,
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
  const sheetId = selected.value === "!lyrics" ? "lyrics" : selected.value
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

function download(sheet: "!lyrics" | SongSheet) {
  const link = document.createElement("a")
  if (sheet === "!lyrics") {
    const blob = new Blob([props.version.lyrics ?? ""], { type: "text/plain" })
    link.href = URL.createObjectURL(blob)
    link.download = `${props.title}.txt`
  } else {
    let ext = "unknown"
    if (sheet.object_type === "application/pdf") ext = "pdf"
    else if (sheet.object_type === "text/plain") ext = "txt"
    link.href = `/api/songs/${props.version.song_id}/versions/${props.version.id}/sheets/${sheet.id}/doc`
    link.download = `${props.title} (${sheet.key}).${ext}`
  }

  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>
