<template>
  <div>
    <Head><Title>History - MusicTeam</Title></Head>
    <h1>History</h1>

    <div class="flex flex-row">
      <h2 class="grow">Top 50 Songs</h2>
      <MtDropdown button-class="btn-gray">
        <template #dropdown-button> Ranking: {{ rankLabels[ranking] }} </template>

        <MtDropdownRadioGroup v-model="ranking" :choices="rankLabels" />
      </MtDropdown>
    </div>
    <MtTable
      v-if="topSongs"
      :columns="columns"
      :data="topSongs.songs"
      :row-click="async (row) => await navigateTo(`/songs/${row.id}`)"
    >
      <template #title="{ row }">
        <NuxtLink :to="`/songs/${row.id}`" class="font-semibold hover:underline">
          {{ row.title }}
        </NuxtLink>
      </template>
      <template #authors="{ row }">
        <span v-for="author in trimArray(row.authors)" :key="author" class="spn-tag">
          {{ author }}
        </span>
      </template>
      <template #appearances="{ row }">
        {{
          row.appearances === Math.trunc(row.appearances)
            ? row.appearances
            : row.appearances.toFixed(3)
        }}
      </template>
      <template #sparkline="{ row }">
        <MtSparkline v-if="sparklines.data" :data="sparklines.data.songs[row.id]" />
      </template>
    </MtTable>
  </div>
</template>

<script setup lang="ts">
import { useHistoryTopSongsStore, useHistorySparklineStore } from "@/stores/history"
import { trimArray } from "@/utils"

const topSongsStore = useHistoryTopSongsStore()
const sparklines = useHistorySparklineStore()

const rankLabels = {
  alltime: "All Time",
  recent: "Most Recent",
  weighted: "Weighted Recent",
}

const ranking = ref<"alltime" | "recent" | "weighted">("alltime")
const topSongs = computed(
  () => topSongsStore.get({ ranking: ranking.value }).data.value,
)

const columns = ref([
  { name: "title", title: "Title" },
  { name: "authors", title: "Authors" },
  { name: "appearances", title: "Appearances" },
  { name: "sparkline", title: "History (2 yr)" },
])
</script>
