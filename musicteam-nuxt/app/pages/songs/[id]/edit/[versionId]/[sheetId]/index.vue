<template>
  <div>
    <div class="flex flex-row gap-2">
      <div class="grow">
        <h1>
          <MtText :text="song?.title" loading="w-48" />
          -
          {{ sheetId === "lyrics" ? "Lyrics" : "Song Sheet" }}
        </h1>
        <h2>
          Version:
          <MtText :text="version?.label" loading="w-32" />
        </h2>
      </div>
      <div>
        <button class="btn-gray" @click="save">Save</button>
      </div>
      <div>
        <button class="btn-gray" @click="$router.back()">Cancel</button>
      </div>
    </div>

    <form class="frm-edit frm-grid">
      <label>
        <span>Label</span>
        <MtSelectOther
          v-model="inputLabel"
          :options="['From CCLI', 'From Library', 'From Hymnal', 'Updated']"
        />
      </label>

      <label>
        <span>Verse Order</span>
        <MtArrayInput v-model="inputVerseOrder" />
      </label>
    </form>

    <div v-if="sheetId === 'lyrics'" class="flex flex-col">
      <textarea v-model="inputLyrics" class="txt-panel"></textarea>
    </div>

    <template v-else>
      <form class="frm-edit frm-grid">
        <label>
          <span>Music Sheet Type <span class="spn-req">*</span></span>
          <MtSelectOther
            v-model="inputSheetType"
            :options="['Chord', 'Lead', 'Vocal', 'Hymn']"
          />
        </label>

        <label>
          <span>Musical Key <span class="spn-req">*</span></span>
          <input v-model="inputKey" class="inp-text" required placeholder="C" />
        </label>

        <label>
          <span>Does music sheet already include verse order?</span>
          <select v-model="inputAutoVerseOrder" class="sel-dropdown">
            <option value="true">Sheet does not have verse order</option>
            <option value="false">Sheet already has verse order</option>
          </select>
        </label>
      </form>

      <SongPdfEditor
        v-if="sheet?.object_type === 'application/pdf'"
        :song-id="id as string"
        :version-id="versionId as string"
        :sheet-id="sheetId as string"
        @has-save="(save) => (saveSheetObject = save)"
      />
      <SongTextEditor
        v-else-if="sheet?.object_type === 'text/plain'"
        :song-id="id as string"
        :version-id="versionId as string"
        :sheet-id="sheetId as string"
        @has-save="(save) => (saveSheetObject = save)"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"
import {
  useSongStore,
  useSongVersionStore,
  useSongSheetStore,
  useSongRefreshStore,
} from "@/stores/songs"
import { fileToBase64String } from "@/utils"

const songStore = useSongStore()
const versionStore = useSongVersionStore()
const sheetStore = useSongSheetStore()
const refreshStore = useSongRefreshStore()

const { id, versionId, sheetId } = useRoute().params

const song = songStore.get({ songId: id as string }).data
const version = versionStore.get({
  songId: id as string,
  versionId: versionId as string,
}).data
const sheet =
  sheetId !== "lyrics"
    ? sheetStore.get({
        songId: id as string,
        versionId: versionId as string,
        sheetId: sheetId as string,
      }).data
    : undefined

const inputLabel = ref<string>()
const inputVerseOrder = ref<string[]>([])
const inputLyrics = ref<string | null>()

watch(
  version,
  () => {
    if (version.value) {
      inputLabel.value = version.value.label
      inputVerseOrder.value = version.value.verse_order?.split(/\s+/) ?? []
      inputLyrics.value = version.value.lyrics
    }
  },
  { immediate: true },
)

const inputSheetType = ref<string>()
const inputKey = ref<string>()
const inputAutoVerseOrder = ref<string>("true")

if (sheet) {
  watch(
    sheet,
    () => {
      if (sheet?.value) {
        inputSheetType.value = sheet.value.type
        inputKey.value = sheet.value.key
        inputAutoVerseOrder.value = sheet.value.auto_verse_order ? "true" : "false"
      }
    },
    { immediate: true },
  )
}

const saveSheetObject = ref<() => Promise<Blob>>()

async function save() {
  await useToaster(async () => {
    const label = inputLabel.value
    const verseOrder = inputVerseOrder.value.join(" ")
    const lyrics = inputLyrics.value

    if (
      label !== version.value?.label ||
      verseOrder !== version.value?.verse_order ||
      lyrics !== version.value?.lyrics
    ) {
      await api.songs.updateSongVersion(id as string, versionId as string, {
        label,
        verse_order: verseOrder,
        lyrics,
      })
    }

    if (saveSheetObject.value) {
      const data = await saveSheetObject.value()
      const encodedFile = await fileToBase64String(data)
      const response = await api.objects.uploadFile(encodedFile, { base64: true })

      await api.songs.updateSongSheet(
        id as string,
        versionId as string,
        sheetId as string,
        {
          type: inputSheetType.value,
          key: inputKey.value,
          auto_verse_order: inputAutoVerseOrder.value === "true",
          object_id: response.data.id,
        },
      )
    }

    await refreshStore.refresh({ songId: id as string })
  })

  await navigateTo({ path: `/songs/${id as string}` })
}
</script>
