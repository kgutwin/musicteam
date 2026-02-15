<template>
  <div>
    <Head>
      <Title>
        {{ copy ? "Copy" : "Edit" }}
        {{ sheetId === "lyrics" ? "Lyrics" : "Song Sheet" }} - MusicTeam
      </Title>
    </Head>

    <div class="flex flex-row gap-2">
      <div class="grow">
        <h1>
          {{ copy ? "Copy" : "Edit" }}
          <MtText :text="song?.title" loading="w-48" />
          -
          {{
            copy === "version"
              ? "Song Version"
              : sheetId === "lyrics"
                ? "Lyrics"
                : "Song Sheet"
          }}
        </h1>
        <h2>
          Version:
          <MtText :text="version?.label" loading="w-32" />
        </h2>
      </div>
      <div>
        <button class="btn-gray" data-cy="save" @click="save">Save</button>
      </div>
      <div>
        <button class="btn-gray" data-cy="cancel" @click="$router.back()">
          Cancel
        </button>
      </div>
    </div>

    <form
      v-if="sheetId === 'lyrics' || copy === 'version'"
      class="frm-edit frm-grid mb-4"
    >
      <label>
        <span>Version Label</span>
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
      <textarea
        v-model="inputLyrics"
        class="txt-panel"
        :placeholder="'Song Title\n\nVerse 1\nYou are...'"
      ></textarea>
    </div>

    <template v-else>
      <form class="frm-edit frm-grid mb-4">
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

      <div class="grid gap-4" :class="copy === 'version' ? 'r-2-col' : 'grid-cols-1'">
        <div>
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
        </div>
        <div v-if="copy === 'version'">
          <h2>Lyrics</h2>
          <div class="mt-2 flex flex-col">
            <textarea
              v-model="inputLyrics"
              class="txt-panel h-[46rem]"
              :placeholder="'Song Title\n\nVerse 1\nYou are...'"
              data-cy="song-lyrics-editor"
            ></textarea>
          </div>
        </div>
      </div>
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

import type { UpdateSongSheet } from "@/services/api"

const songStore = useSongStore()
const versionStore = useSongVersionStore()
const sheetStore = useSongSheetStore()
const refreshStore = useSongRefreshStore()

const { mustHave } = useRole()
const { id, versionId, sheetId } = useRoute().params
const { copy } = useRoute().query

mustHave("leader", `/songs/${id}`)

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
      if (version.value.verse_order)
        inputVerseOrder.value = version.value.verse_order.split(/\s+/)
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

async function saveSheet() {
  if (!saveSheetObject.value) {
    return undefined
  }

  const data = await saveSheetObject.value()
  const encodedFile = await fileToBase64String(data)
  const response = await api.objects.uploadFile(encodedFile, { base64: true })
  return response.data.id
}

async function saveNew() {
  await useToaster(async () => {
    let newVersionId = versionId as string
    if (copy === "version") {
      if (!inputLabel.value) throw new Error("missing song version label")

      const newVersion = await api.songs.newSongVersion(id as string, {
        label: inputLabel.value,
        verse_order: inputVerseOrder.value.join(" "),
        lyrics: inputLyrics.value,
      })
      newVersionId = newVersion.data["id"]
    }

    const destQuery: Record<string, string> = { version: newVersionId }

    if (sheet && sheet.value) {
      const objectId = (await saveSheet()) ?? sheet.value.object_id
      const objectType = sheet.value.object_type

      if (!objectId) throw new Error("missing object ID")
      if (!objectType) throw new Error("missing object type")
      if (!inputSheetType.value) throw new Error("missing song sheet type")
      if (!inputKey.value) throw new Error("missing song key")

      const newSheet = await api.songs.newSongSheet(id as string, newVersionId, {
        type: inputSheetType.value,
        key: inputKey.value,
        auto_verse_order: inputAutoVerseOrder.value === "true",
        object_id: objectId,
        object_type: objectType,
      })

      destQuery.sheet = newSheet.data["id"]
    }

    await refreshStore.refresh({ songId: id as string })

    await navigateTo({
      path: `/songs/${id as string}`,
      query: destQuery,
    })
  })
}

async function saveEdit() {
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

    if (sheetId !== "lyrics") {
      const update: UpdateSongSheet = {
        type: inputSheetType.value,
        key: inputKey.value,
        auto_verse_order: inputAutoVerseOrder.value === "true",
        object_id: await saveSheet(),
      }

      await api.songs.updateSongSheet(
        id as string,
        versionId as string,
        sheetId as string,
        update,
      )
    }

    await refreshStore.refresh({ songId: id as string })
  })

  await navigateTo({
    path: `/songs/${id as string}`,
    query: { version: versionId as string, sheet: sheetId },
  })
}

async function save() {
  if (copy) {
    return await saveNew()
  } else {
    return await saveEdit()
  }
}
</script>
