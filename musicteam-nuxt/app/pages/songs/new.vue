<template>
  <div>
    <Head>
      <Title v-if="existingSongVersionId">Add Song Sheet - MusicTeam</Title>
      <Title v-else-if="existingSongId">Add Song Version - MusicTeam</Title>
      <Title v-else>New Song - MusicTeam</Title>
    </Head>

    <h1 v-if="existingSongVersionId">Add Song Sheet</h1>
    <h1 v-else-if="existingSongId">Add Song Version</h1>
    <h1 v-else>New Song</h1>

    <form class="frm-edit" :disabled="!!existingSongId">
      <label>
        <span>Title <span class="spn-req">*</span></span>
        <input
          v-model="inputTitle"
          :disabled="!!existingSongId"
          class="inp-text"
          required
        />
        <SongNewLibraryLinks v-if="!existingSongId" :title="inputTitle" />
      </label>

      <label>
        <span>Authors <span class="spn-req">*</span></span>
        <MtArrayInput v-model="inputAuthors" :disabled="!!existingSongId" allow-space />
      </label>

      <label>
        <span>CCLI Number</span>
        <input
          v-model="inputCcliNum"
          :disabled="!!existingSongId"
          class="inp-text"
          type="text"
          inputmode="numeric"
          pattern="\d*"
        />
        <SongNewLibraryLinks v-if="!existingSongId" :ccli-num="inputCcliNum" />
      </label>

      <label>
        <span>Tags</span>
        <MtArrayInput v-model="inputTags" :disabled="!!existingSongId" allow-space />
      </label>
    </form>

    <form class="frm-edit" :disabled="!!existingSongVersionId">
      <label v-if="!existingSongId" class="flex !flex-row-reverse text-sm items-center">
        <span>Not available</span>
        <input
          type="checkbox"
          v-model="inputVersionUnavailable"
          :disabled="!!existingSongVersionId"
        />
      </label>

      <template v-if="!inputVersionUnavailable">
        <label>
          <span>Version Label <span class="spn-req">*</span></span>
          <MtSelectOther
            v-model="inputLabel"
            :options="['From CCLI', 'From Library', 'From Hymnal', 'Updated']"
            :disabled="!!existingSongVersionId"
          />
        </label>

        <label>
          <span>Verse Order <span class="spn-req">*</span></span>
          <MtArrayInput v-model="inputVerseOrder" :disabled="!!existingSongVersionId" />
        </label>

        <label>
          <div class="flex flex-row gap-4">
            <span>Lyrics <span class="spn-req">*</span></span>
            <span v-if="inputCcliNum">
              <a
                :href="`https://songselect.ccli.com/songs/${inputCcliNum}`"
                target="_blank"
                class="a-hov"
              >
                SongSelect
                <Icon name="solar:square-share-line-outline" size="12" class="ml-2" />
              </a>
            </span>
          </div>
          <textarea
            v-model="inputLyrics"
            :disabled="!!existingSongVersionId"
            class="txt-lg"
            rows="12"
            required
          />
        </label>
      </template>
    </form>

    <div
      class="grid gap-x-4"
      :class="{
        'grid-cols-1': inputSheets.length <= 1,
        'grid-cols-2': inputSheets.length > 1,
      }"
    >
      <SongNewSheetForm
        v-for="(sheet, index) in inputSheets"
        v-model="inputSheets[index]"
        @remove="
          () => {
            inputSheets = inputSheets.toSpliced(index, 1)
          }
        "
      />
    </div>

    <div class="flex flex-row gap-2 mt-4">
      <button
        class="btn-gray"
        @click="save"
        :disabled="invalid || saveStatus === 'pending' || saveStatus === 'ok'"
      >
        Save
        <Icon
          v-if="saveStatus === 'pending'"
          name="svg-spinners:270-ring-with-bg"
          class="ml-4"
        />
      </button>
      <button class="btn-gray" @click="addSheet">
        <div class="flex flex-row gap-2 items-center">
          <Icon name="ri:add-large-fill" /> Add another sheet
        </div>
      </button>
      <button class="btn-gray" @click="cancel">Cancel</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"
import { useSongStore, useSongVersionStore, useSongRefreshStore } from "@/stores/songs"
import { fileToBase64String } from "@/utils"

import type { NewSongSheet } from "@/services/api"
import type { ToasterStatus } from "@/types/toast"

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
const inputVersionUnavailable = ref(false)
watch(inputVersionUnavailable, (newV) => {
  if (newV) {
    inputLabel.value = "Incomplete"
  }
})

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

const inputSheets = ref<Partial<NewSongSheet>[]>([{}])
const inputSheetsValid = computed<boolean>(() => {
  for (const sheet of inputSheets.value) {
    if (!sheet.type || !sheet.key || !sheet.object_id || !sheet.object_type)
      return false
  }
  return true
})

function addSheet() {
  inputSheets.value = [...inputSheets.value, {}]
}

const invalid = useInvalid(
  [inputTitle, inputAuthors, inputLabel, inputSheetsValid],
  [
    inputCcliNum,
    inputTags,
    inputVerseOrder,
    inputLyrics,
    inputVersionUnavailable,
    inputSheets,
  ],
)

const songRefresh = useSongRefreshStore()

const saveStatus = ref<ToasterStatus>()

async function save() {
  const finalSongId = await useToaster(
    async () => {
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

        if (!title) throw new Error("no title")

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

        if (!label) throw new Error("no label")

        const versionResponse = await api.songs.newSongVersion(songId, {
          label,
          verse_order: verseOrder,
          lyrics,
        })

        versionId = versionResponse.data.id
      }

      const promises = []

      for (const sheet of inputSheets.value) {
        if (sheet.type && sheet.key && sheet.object_id && sheet.object_type) {
          promises.push(
            await api.songs.newSongSheet(songId, versionId, sheet as NewSongSheet),
          )
        }
      }
      await Promise.all(promises)

      await songRefresh.refresh({ songId })
      return songId
    },
    { errorTitle: "Could not save song", status: saveStatus },
  )

  await navigateTo({ path: `/songs/${finalSongId}` })
}

async function cancel() {
  const path = existingSongId ? `/songs/${existingSongId}` : "/songs"
  await navigateTo({ path })
}
</script>
