<template>
  <div>
    <Head><Title>Search Songs - MusicTeam</Title></Head>
    <div class="md:flex flex-row gap-16 items-baseline mb-8">
      <h1>Search Songs</h1>
      <div class="rounded bg-sky-100 px-8 py-4 shadow-lg grow">
        <form @submit.prevent="doSearch" class="flex flex-row gap-4">
          <input
            type="search"
            v-model="ss.query"
            placeholder="Word or phrase..."
            class="inp-text grow"
          />
          <button class="btn-gray" :disabled="!ss.query || searching">Search</button>
        </form>
      </div>
    </div>

    <h2 v-if="searching">
      Searching
      <Icon name="svg-spinners:3-dots-fade" />
    </h2>
    <h2 v-else-if="ss.results">{{ ss.results.hits.length }} songs found</h2>

    <div class="divide-y">
      <NuxtLink
        :to="`/songs/${hit.song.id}`"
        v-for="hit in ss.results?.hits ?? []"
        class="block hover:bg-gray-100 p-4"
      >
        <SongSearchHit :hit="hit" />
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"
import { useSearchStore } from "@/stores/search"

import type { SearchSongList } from "@/services/api"

const ss = useSearchStore()

const searching = ref(false)

async function doSearch() {
  if (searching.value) return

  searching.value = true
  await useToaster(async () => {
    if (!ss.query) return
    const resp = await api.songs.searchSongs({ q: ss.query })
    ss.results = resp.data
  })
  searching.value = false
}
</script>
