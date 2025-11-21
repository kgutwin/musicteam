<template>
  <div>
    <Head>
      <Title>{{ song?.title ?? "Song" }} - MusicTeam</Title>
    </Head>

    <div class="flex flex-col sm:flex-row gap-4 w-full">
      <div class="div-panel basis-4/6">
        <div class="flex flex-row">
          <div class="basis-4/6">
            <h1>
              <MtEditable :model="song" prop="title" wide @save="saveSong('title')" />
            </h1>
            <h3>
              <MtEditable :model="song" prop="authors" @save="saveSong('authors')">
                <template #input="{ modelValue, updateModelValue }">
                  <MtArrayInput
                    :modelValue="modelValue"
                    @update:modelValue="updateModelValue"
                    allow-space
                  />
                </template>
              </MtEditable>
            </h3>
            <div class="italic">
              CCLI Number:
              <template v-if="song?.ccli_num">
                <MtEditable :model="song" prop="ccli_num" @save="saveSong('ccli_num')">
                  <a
                    :href="`https://songselect.ccli.com/songs/${song.ccli_num}`"
                    target="_blank"
                    class="a-hov"
                  >
                    {{ song.ccli_num }}
                    <Icon name="solar:square-top-down-outline" size="12" class="ml-2" />
                  </a>
                </MtEditable>
              </template>
              <template v-else>
                <MtEditable :model="song" prop="ccli_num" @save="saveSong('ccli_num')">
                  Unknown
                </MtEditable>
              </template>
            </div>
          </div>
          <div class="basis-2/6 text-right">
            <div class="mb-2 flex flex-row-reverse gap-4 items-end">
              <MtDropdown button-class="btn-red">
                <template #dropdown-button>Delete</template>
                <button
                  :disabled="!selectedSheet"
                  class="flex flex-col"
                  @click="deleteSheet"
                >
                  <span>Delete Sheet:</span>
                  <span class="italic ml-1">
                    {{
                      selectedSheet
                        ? `${selectedSheet.type} (${selectedSheet.key})`
                        : "No sheet selected"
                    }}
                  </span>
                </button>
                <button
                  class="flex flex-col"
                  :disabled="(versions?.song_versions ?? []).length <= 1"
                  @click="deleteVersion"
                >
                  <span>Delete Version:</span>
                  <span
                    v-if="(versions?.song_versions ?? []).length <= 1"
                    class="italic ml-1"
                    >Cannot delete the only version</span
                  >
                  <span v-else class="italic ml-1">{{ version?.label }}</span>
                </button>
                <button class="text-red-500" @click="deleteSong">Delete Song</button>
              </MtDropdown>
              <button @click="shareSong" class="btn-icon" title="Share...">
                <Icon name="solar:share-outline" />
              </button>
            </div>
            <MtEditableTags :model="song" @save="saveSong('tags')" />
          </div>
        </div>

        <hr />

        <div class="text-sm">
          Uploaded on {{ localdate(song?.created_on) }}
          <template v-if="user?.name">by {{ user?.name }}</template>

          <template v-if="song && version && version.creator_id !== song.creator_id">
            - Version {{ version.label }} created on
            {{ localdate(version.created_on) }} by
            {{ userStore.get({ userId: version.creator_id })?.data?.value?.name }}
          </template>
        </div>
      </div>

      <div class="div-panel basis-2/6">
        <div class="flex flex-row items-baseline">
          <h2 class="grow">Versions</h2>
          <button class="btn-gray" @click="addVersion">
            <Icon name="ri:add-large-line" class="show-lg" />
            <span class="hide-lg">Add Version...</span>
          </button>
        </div>
        <ul class="list-disc ml-4 mt-1">
          <li v-if="versions?.song_versions === undefined">
            <MtText loading="w-32" />
          </li>
          <li v-for="version in versions?.song_versions ?? []" :key="version.id">
            <button
              @click="selectedVersion = version.id"
              class="inline-block w-full text-left rounded p-1 hover:bg-blue-100 hover:shadow-lg"
            >
              <div :class="{ 'font-bold': version.id === selectedVersion }">
                <MtEditable
                  :model="version"
                  prop="label"
                  @save="saveVersion(version, 'label')"
                >
                  {{ version.label }}
                </MtEditable>
                ({{ localdate(version.created_on) }})
              </div>
              <div>
                Verse order:
                <MtEditable
                  :model="version"
                  prop="verse_order"
                  @save="saveVersion(version, 'verse_order')"
                >
                  <template #input="{ modelValue, updateModelValue }">
                    <MtArrayInput
                      :modelValue="modelValue?.split(/\s+/)"
                      @update:modelValue="(arr) => updateModelValue(arr.join(' '))"
                    />
                  </template>
                </MtEditable>
              </div>
            </button>
          </li>
        </ul>
      </div>
    </div>

    <SongVersionPanel
      v-if="song && version"
      :title="song.title"
      :version="version"
      @selected="(sheet) => (selectedSheet = sheet)"
    />
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"
import {
  useSongStore,
  useSongVersionlistStore,
  useSongRefreshStore,
} from "@/stores/songs"
import { useUserStore } from "@/stores/users"
import { localdate } from "@/utils"

import type { Song, SongVersion, SongSheet } from "@/services/api"

const songStore = useSongStore()
const userStore = useUserStore()
const versionsStore = useSongVersionlistStore()
const refreshStore = useSongRefreshStore()

const { id } = useRoute().params

const song = songStore.get({ songId: id as string }).data
const versions = versionsStore.get({ songId: id as string }).data
const user = computed(() => {
  const userId = song.value?.creator_id
  if (userId) {
    return userStore.get({ userId }).data.value
  }
  return undefined
})

const selectedVersion = ref<string>()
const selectedSheet = ref<SongSheet>()

const version = computed(() => {
  if (versions.value && selectedVersion.value) {
    const found = versions.value.song_versions.find(
      (v) => v.id === selectedVersion.value,
    )
    if (found) return found
  }
  return undefined
})

watchEffect(() => {
  if (versions.value && !selectedVersion.value) {
    const found = versions.value.song_versions[0]
    if (found) selectedVersion.value = found.id
  }
})

async function addVersion() {
  await navigateTo({
    path: "/songs/new",
    query: {
      song: id as string,
    },
  })
}

async function deleteSong() {
  if (!window.confirm("Are you sure you want to delete this song?")) return

  await useToaster(async () => await api.songs.deleteSong(id as string), {
    errorTitle: "Could not delete song",
  })

  await navigateTo({ path: "/songs" })
}

async function deleteVersion() {
  const sv = selectedVersion.value
  if (!sv) return

  await useToaster(async () => await api.songs.deleteSongVersion(id as string, sv), {
    errorTitle: "Could not delete song version",
  })

  await refreshStore.refresh({ songId: id as string })

  selectedVersion.value = ""
}

async function deleteSheet() {
  const ssid = selectedSheet.value?.id
  if (!ssid) return
  const sv = selectedVersion.value
  if (!sv) return

  await useToaster(
    async () => await api.songs.deleteSongSheet(id as string, sv, ssid),
    { errorTitle: "Could not delete song sheet " },
  )

  await refreshStore.refresh({ songId: id as string })
}

async function saveSong(field: keyof Song) {
  if (!song.value) return
  await api.songs.updateSong(id as string, { [field]: song.value[field] })
  await refreshStore.refresh({ songId: id as string })
}

async function saveVersion(version: SongVersion, field: keyof SongVersion) {
  await api.songs.updateSongVersion(id as string, version.id, {
    [field]: version[field],
  })
  await refreshStore.refresh({ songId: id as string, versionId: version.id })
}

function shareSong() {
  window.navigator.share({ url: window.location.href, title: song.value?.title })
}
</script>
