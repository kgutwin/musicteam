<template>
  <div>
    <div class="flex flex-row gap-4 w-full">
      <div class="div-panel basis-4/6">
        <div class="flex flex-row">
          <h1 class="grow">{{ song?.title }}</h1>
          <button class="btn-red">Delete</button>
        </div>
        <div class="flex flex-row">
          <h3 class="grow">{{ song?.authors?.join(", ") }}</h3>
          <div>
            <span v-for="tag in song?.tags ?? []" :key="tag" class="spn-tag">
              {{ tag }}
            </span>
          </div>
        </div>
        <div class="italic">CCLI Number: {{ song?.ccli_num ?? "Unknown" }}</div>
        <hr />
        <div class="text-sm">
          Uploaded on {{ localdate(song?.created_on) }} by
          {{ user?.name }}
        </div>
      </div>

      <div class="div-panel basis-2/6">
        <div class="flex flex-row items-baseline">
          <h2 class="grow">Versions</h2>
          <button class="btn-gray" @click="addVersion">Add Version...</button>
        </div>
        <ul class="list-disc ml-4">
          <li
            v-for="version in versions?.song_versions ?? []"
            :key="version.id"
            :class="{ 'font-bold': version.id === selectedVersion }"
          >
            <button @click="selectedVersion = version.id" class="hover:underline">
              {{ version.label }}
            </button>
            ({{ localdate(version.created_on) }})
          </li>
        </ul>
      </div>
    </div>

    <SongVersionPanel v-if="version" :version="version" />
  </div>
</template>

<script setup lang="ts">
import { useSongStore, useSongVersionlistStore } from "@/stores/songs"
import { useUserStore } from "@/stores/users"
import { localdate } from "@/utils"

const songStore = useSongStore()
const userStore = useUserStore()
const versionsStore = useSongVersionlistStore()

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
</script>
