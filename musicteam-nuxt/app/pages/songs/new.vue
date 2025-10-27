<template>
  <div>
    <h1 v-if="existingSongVersionId">Add Song Sheet</h1>
    <h1 v-else-if="existingSongId">Add Song Version</h1>
    <h1 v-else>New Song</h1>

    <form class="frm-edit" :disabled="!!existingSongId">
      <label>
        <span>Title</span>
        <input v-model="inputTitle" :disabled="!!existingSongId" class="inp-text" />
      </label>

      <label>
        <span>Authors</span>
        <MtArrayInput v-model="inputAuthors" :disabled="!!existingSongId" allow-space />
      </label>

      <label>
        <span>CCLI Number</span>
        <input v-model="inputCcliNum" :disabled="!!existingSongId" class="inp-text" />
      </label>

      <label>
        <span>Tags</span>
        <MtArrayInput v-model="inputTags" :disabled="!!existingSongId" allow-space />
      </label>
    </form>

    <form class="frm-edit" :disabled="!!existingSongVersionId">
      <label>
        <span>Label</span>
        <MtSelectOther
          v-model="inputLabel"
          :options="['From CCLI', 'From Library', 'From Hymnal', 'Updated']"
          :disabled="!!existingSongVersionId"
        />
      </label>

      <label>
        <span>Verse Order</span>
        <MtArrayInput v-model="inputVerseOrder" :disabled="!!existingSongVersionId" />
      </label>

      <label>
        <span>Lyrics</span>
        <textarea
          v-model="inputLyrics"
          :disabled="!!existingSongVersionId"
          class="txt-lg"
          rows="12"
        />
      </label>
    </form>

    <form class="frm-edit">
      <label>
        <span>Music Sheet Type</span>
        <MtSelectOther
          v-model="inputSheetType"
          :options="['Chord', 'Lead', 'Vocal', 'Hymn']"
        />
      </label>

      <label>
        <span>Musical Key</span>
        <input v-model="inputKey" class="inp-text" />
      </label>

      <label>
        <span>Select File</span>
        <div class="flex flex-row gap-2">
          <input
            type="file"
            accept="text/plain, application/pdf, application/vnd.recordare.musicxml+xml"
            @change="addFile"
          />
          <div v-if="inputObjectId">* confirmed</div>
        </div>
      </label>
    </form>

    <div class="flex flex-row gap-2">
      <button class="btn-gray" @click="save">Save</button>
      <button class="btn-gray" @click="cancel">Cancel</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"
import { useSongStore, useSongVersionStore, useSongRefreshStore } from "@/stores/songs"

const { song: existingSongId, version: existingSongVersionId } = useRoute().query

const inputTitle = ref<string>()
const inputAuthors = ref<string[]>([])
const inputCcliNum = ref<string>()
const inputTags = ref<string[]>([])

if (existingSongId) {
  const songStore = useSongStore()
  const song = songStore.get({ songId: existingSongId as string }).data

  watch(
    song,
    () => {
      if (song.value) {
        inputTitle.value = song.value.title
        inputAuthors.value = song.value.authors
        inputCcliNum.value = song.value.ccli_num?.toString()
        inputTags.value = song.value.tags ?? []
      }
    },
    { immediate: true },
  )
}

const inputLabel = ref<string>()
const inputVerseOrder = ref<string[]>([])
const inputLyrics = ref<string>()

if (existingSongId && existingSongVersionId) {
  const songVersionStore = useSongVersionStore()
  const songVersion = songVersionStore.get({
    songId: existingSongId as string,
    versionId: existingSongVersionId as string,
  }).data

  watch(
    songVersion,
    () => {
      const ver = songVersion.value
      if (ver) {
        inputLabel.value = ver.label
        inputVerseOrder.value = ver.verse_order?.split(/\s+/) ?? []
        inputLyrics.value = ver.lyrics ?? undefined
      }
    },
    { immediate: true },
  )
}

const inputKey = ref<string>()
const inputSheetType = ref<string>()
const inputObjectId = ref<string>()
const inputObjectType = ref<string>()

const songRefresh = useSongRefreshStore()

function fileToBase64String(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => {
      let encoded = reader.result?.toString() || ""
      encoded = encoded.replace(/^data:(.*,)?/, "")
      if (encoded.length % 4 > 0) {
        encoded += "=".repeat(4 - (encoded.length % 4))
      }
      resolve(encoded)
    }
    reader.onerror = reject
  })
}

async function addFile(event: any) {
  const file = event.target?.files?.[0] as File | undefined
  if (file) {
    inputObjectType.value = file.type
    const encodedFile = await fileToBase64String(file)
    const response = await api.objects.uploadFile(encodedFile, { base64: true })
    inputObjectId.value = response.data.id
  }
}

async function save() {
  let songId: string
  if (existingSongId) {
    songId = existingSongId as string
  } else {
    const title = inputTitle.value
    const authors = inputAuthors.value
    const ccliNum = Number.isNaN(parseInt(inputCcliNum.value ?? ""))
      ? null
      : parseInt(inputCcliNum.value!)
    const tags = inputTags.value

    if (!title) return

    const songResponse = await api.songs.newSong({
      title,
      authors,
      ccli_num: ccliNum,
      tags,
    })

    songId = songResponse.data.id
  }

  let versionId: string
  if (existingSongVersionId) {
    versionId = existingSongVersionId as string
  } else {
    const label = inputLabel.value
    const verseOrder = inputVerseOrder.value.join(" ")
    const lyrics = inputLyrics.value

    if (!label) return

    const versionResponse = await api.songs.newSongVersion(songId, {
      label,
      verse_order: verseOrder,
      lyrics,
    })

    versionId = versionResponse.data.id
  }

  const sheetType = inputSheetType.value
  const key = inputKey.value
  const objectId = inputObjectId.value
  const objectType = inputObjectType.value

  if (!sheetType) return
  if (!key) return
  if (!objectId) return
  if (!objectType) return

  await api.songs.newSongSheet(songId, versionId, {
    type: sheetType,
    key,
    object_id: objectId,
    object_type: objectType,
  })

  await songRefresh.refresh({ songId })

  await navigateTo({ path: `/songs/${songId}` })
}

async function cancel() {
  const path = existingSongId ? `/songs/${existingSongId}` : "/songs"
  await navigateTo({ path })
}
</script>
