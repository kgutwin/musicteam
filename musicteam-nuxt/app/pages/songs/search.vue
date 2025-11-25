<template>
  <div>
    <Head><Title>Search Songs - MusicTeam</Title></Head>
    <div class="flex flex-row gap-16 items-baseline mb-8">
      <h1>Search Songs</h1>
      <div class="rounded bg-sky-100 px-8 py-4 shadow-lg grow">
        <form @submit.prevent="doSearch" class="flex flex-row gap-4">
          <input
            type="search"
            v-model="query"
            placeholder="Word or phrase..."
            class="inp-text grow"
          />
          <button class="btn-gray" :disabled="!query">Search</button>
        </form>
      </div>
    </div>

    <div class="divide-y">
      <NuxtLink
        :to="`/songs/${hit.song.id}`"
        v-for="hit in searchResults?.hits ?? []"
        class="block hover:bg-gray-100 p-4"
      >
        <SongSearchHit :hit="hit" />
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"

import type { SearchSongList } from "@/services/api"

const query = ref<string>()
const searchResults = ref<SearchSongList>()

async function doSearch() {
  useToaster(async () => {
    if (!query.value) return
    const resp = await api.songs.searchSongs({ q: query.value })
    searchResults.value = resp.data
  })
}
</script>
