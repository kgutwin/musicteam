<template>
  <div>
    <SongVersionPanelCommentsMedia
      :song-id="version.song_id"
      :version-id="version.id"
      class="my-4"
    />

    <MtTabPanel
      v-model="selected"
      :loading="sheets?.song_sheets === undefined || sheetsStatus === 'pending'"
      :options="sheetTabs"
    >
      <template #tab-button="{ opt }">
        <div class="flex flex-row gap-2">
          <div>{{ opt.title }}</div>
          <div v-if="(opt?.tags?.length ?? 0) > 0">
            <span
              v-for="tag in opt.tags"
              :key="tag"
              class="spn-tag text-gray-500 text-xs"
            >
              {{ tag }}
            </span>
          </div>
        </div>
      </template>

      <button class="mr-4 btn-icon" title="Download" @click="download(selectedSheet)">
        <Icon name="solar:download-minimalistic-bold" />
      </button>
      <MtDropdown v-if="canEdit" button-class="btn-gray" data-cy="edit-sheet">
        <template #dropdown-button>
          <Icon name="ri:edit-2-line" class="show-lg" />
          <span class="hide-lg"> Edit / Copy </span>
        </template>
        <button v-if="selectedSheet !== '!lyrics'" @click="edit('copySheet')">
          Copy to New Sheet
        </button>
        <button @click="edit('copyVersion')">Copy to New Version</button>
        <button @click="edit('edit')">Edit Current Version</button>
      </MtDropdown>
      <button
        v-if="canEdit"
        class="btn-gray max-sm:h-8"
        data-cy="add-sheet"
        @click="addSheet"
      >
        <Icon name="ri:add-large-line" class="show-lg" />
        <span class="hide-lg">Add Sheet...</span>
      </button>
      <template v-if="canLead && activeSetlistStore.setlist">
        <button
          v-if="existingSongSetlistSheet === undefined"
          :disabled="selectedSheet === '!lyrics'"
          :title="
            selectedSheet === '!lyrics'
              ? 'Choose a music sheet to add to the set list'
              : ''
          "
          class="btn-gray max-sm:h-8"
          @click="() => addToPosition('candidate')"
        >
          <Icon name="ri:play-list-add-line" class="show-lg" />
          <span class="hide-lg">Add to Set List</span>
          <Icon
            v-if="addSetlistStatus === 'pending'"
            name="svg-spinners:3-dots-fade"
            class="ml-2"
          />
        </button>
        <MtDropdown v-else button-class="btn-gray">
          <template #dropdown-button>
            <Icon name="ri:play-list-add-line" class="show-lg" />
            <span class="hide-lg">Add to Set List</span>
            <Icon
              v-if="addSetlistStatus === 'pending'"
              name="svg-spinners:3-dots-fade"
              class="ml-2"
            />
          </template>
          <button @click="() => addToPosition('replace')">Replace Existing</button>
          <button @click="() => addToPosition('secondary')">Add as Secondary</button>
          <button @click="() => addToPosition('candidate')">Add as Candidate</button>
        </MtDropdown>
      </template>
    </MtTabPanel>

    <SongTextPanel
      v-if="selectedSheet === '!lyrics'"
      :verse-order="version.verse_order"
    >
      <template #copy>
        <MtCopyToClipboard
          class="pr-4 pb-2 btn-icon text-blue-500 hover:text-blue-700"
          :content="lyricsToClipboard"
        />
      </template>

      {{ version.lyrics ?? "Lyrics are missing, use the Edit button to add them!" }}
    </SongTextPanel>
    <SongTextPanel
      v-else-if="selectedSheet.object_type === 'text/plain'"
      :verse-order="selectedSheet.auto_verse_order ? version.verse_order : null"
    >
      <SongText
        :song-id="version.song_id"
        :version-id="version.id"
        :sheet-id="selectedSheet.id"
      />
    </SongTextPanel>
    <template v-else>
      <object
        :data="`/api/songs/${version.song_id}/versions/${version.id}/sheets/${selectedSheet.id}/doc`"
        class="w-full h-screen"
      ></object>
      <button
        v-if="isMobileSafari()"
        class="block w-full p-2 rounded-b shadow bg-violet-200 text-center"
        @click="download(selectedSheet)"
      >
        Open full sheet
      </button>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useModal } from "tailvue"

import type { SongVersion, SongSheet, NewSetlistSheet } from "@/services/api"
import { api } from "@/services"
import { useSongSheetlistStore } from "@/stores/songs"
import { useActiveSetlistStore, useSetlistSheetlistStore } from "@/stores/setlists"
import { isMobileSafari } from "@/utils"

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

const { canEdit, canLead } = useRole()

const sheets = computed(
  () =>
    sheetsStore.get({
      songId: props.version.song_id,
      versionId: props.version.id,
    }).data.value,
)

const sheetsStatus = computed(
  () =>
    sheetsStore.get({ songId: props.version.song_id, versionId: props.version.id })
      .status.value,
)

interface SheetTab {
  name: string
  title: string
  tags?: string[]
}

const sheetTabs = computed<SheetTab[]>(() => {
  return [{ name: "!lyrics", title: "Lyrics" }].concat(
    (sheets.value?.song_sheets ?? []).map((s) => ({
      name: s.id,
      title: `${s.type} (${s.key})`,
      tags: s.tags,
    })),
  )
})
const selected = ref<string>((query.sheet as string) ?? "!lyrics")
const selectedSheet = computed<"!lyrics" | SongSheet>(
  () => sheets.value?.song_sheets?.find((s) => s.id === selected.value) ?? "!lyrics",
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

const addSetlistStatus = ref<ToasterStatus>()

const existingSongSetlistSheet = computed(() => {
  const setlist = activeSetlistStore.setlist
  if (!setlist) return undefined

  const setlistSheetlist = setlistSheetlistStore.get({ setlistId: setlist.id }).data
    .value
  if (!setlistSheetlist) return undefined
  return setlistSheetlist.sheets
    .sort((a, b) => a.type.localeCompare(b.type))
    .find((sheet) => sheet.song_id === props.version.song_id)
})

async function addToPosition(mode: "replace" | "secondary" | "candidate") {
  const setlist = activeSetlistStore.setlist
  if (!setlist) return
  if (selectedSheet.value === "!lyrics") return

  const req: NewSetlistSheet = {
    type: "5:candidate",
    song_sheet_id: selected.value,
  }

  const exSheet = existingSongSetlistSheet.value
  if (exSheet) {
    if (mode === "replace") {
      req.setlist_position_id = exSheet.setlist_position_id
      req.type = exSheet.type
    } else if (mode === "secondary") {
      req.setlist_position_id = exSheet.setlist_position_id
      req.type = exSheet.setlist_position_id ? "2:secondary" : "5:candidate"
    }
  }

  await useToaster(
    async () => {
      await api.setlists.newSetlistSheet(setlist.id, req)

      if (mode === "replace" && exSheet) {
        await api.setlists.deleteSetlistSheet(setlist.id, exSheet.id)
      }

      await setlistSheetlistStore.refresh({ setlistId: setlist.id })
    },
    { status: addSetlistStatus },
  )
}

function lyricsToClipboard() {
  if (props.version.lyrics) return props.version.lyrics
}

async function edit(mode: "edit" | "copyVersion" | "copySheet") {
  const sheetId = selected.value === "!lyrics" ? "lyrics" : selected.value
  const query =
    mode === "copyVersion"
      ? { copy: "version" }
      : mode === "copySheet"
        ? { copy: "sheet" }
        : {}
  await navigateTo({
    path: `/songs/${props.version.song_id}/edit/${props.version.id}/${sheetId}`,
    query,
  })
}

// function edit() {
//   const modal = useModal()
//
//   modal.show({
//     title: "What would you like to do?",
//     body:
//       "If you have a new set of lyrics, a new verse order, or a new song sheet, " +
//       "it's probably best to click Copy to a New Version. If you are correcting a " +
//       "mistake, click Edit Current Version.",
//     primary: {
//       label: "Copy to a New Version",
//       theme: "blue",
//       action: async () =>
//         await navigateTo({
//           path: "/songs/new",
//           query: {
//             song: props.version.song_id,
//             version: props.version.id,
//             copy: "true",
//           },
//         }),
//     },
//     secondary: {
//       label: "Edit Current Version",
//       theme: "white",
//       action: editCurrentVersion,
//     },
//   })
// }

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

const commentsOpen = ref(false)
</script>
