<template>
  <div>
    <Head>
      <Title>{{ song?.title ?? "Song" }} - MusicTeam</Title>
    </Head>

    <div class="flex flex-row gap-4 w-full">
      <div class="div-panel basis-4/6">
        <div class="flex flex-row">
          <div class="basis-1/2">
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
                    <Icon
                      name="solar:square-share-line-outline"
                      size="12"
                      class="ml-2"
                    />
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
          <div class="basis-1/2 text-right">
            <div class="mb-2">
              <button class="btn-red" @click="deleteSong">Delete</button>
            </div>
            <MtEditable :model="song" prop="tags" @save="saveSong('tags')">
              <div class="flex flex-row flex-wrap">
                <span
                  v-if="(song?.tags ?? []).length === 0"
                  class="italic text-gray-400"
                >
                  No tags
                </span>
                <span v-for="tag in song?.tags ?? []" :key="tag" class="spn-tag">
                  {{ tag }}
                </span>
              </div>

              <template #input="{ modelValue, updateModelValue }">
                <MtArrayInput
                  class="min-w-24"
                  :modelValue="modelValue"
                  @update:modelValue="updateModelValue"
                  allow-space
                />
              </template>
            </MtEditable>
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
          <button class="btn-gray" @click="addVersion">Add Version...</button>
        </div>
        <ul class="list-disc ml-4">
          <li v-if="versions?.song_versions === undefined">
            <MtText loading="w-32" />
          </li>
          <li v-for="version in versions?.song_versions ?? []" :key="version.id">
            <div :class="{ 'font-bold': version.id === selectedVersion }">
              <MtEditable
                :model="version"
                prop="label"
                @save="saveVersion(version, 'label')"
              >
                <button @click="selectedVersion = version.id" class="hover:underline">
                  {{ version.label }}
                </button>
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
          </li>
        </ul>
      </div>
    </div>

    <SongVersionPanel v-if="version" :version="version" />
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

import type { Song, SongVersion } from "@/services/api"

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

  await useToaster(async () => await api.songs.deleteSong(id as string))

  await navigateTo({ path: "/songs" })
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
</script>
