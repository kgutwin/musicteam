<template>
  <div>
    <Head><Title>Songs - MusicTeam</Title></Head>
    <div class="flex flex-row items-stretch gap-2 flex-wrap sm:flex-nowrap">
      <h1 class="grow hide-md order-1">Songs</h1>
      <div v-if="numSongs" class="self-center order-2">
        <template v-if="numSongs.filtered !== numSongs.total">
          {{ numSongs.filtered }} of
        </template>
        {{ numSongs.total }} songs
      </div>
      <input
        v-model="prefs.filters.title"
        type="search"
        placeholder="Filter by Title"
        class="inp-text grow sm:grow-0 order-3 w-12 sm:w-32"
      />
      <div class="sm:hidden basis-full order-4 min-[320px]:max-[390px]:order-7"></div>
      <div class="hidden min-[390px]:max-sm:block grow order-5"></div>
      <MtDropdown
        :button-class="`btn-gray ` + (hasFilters ? `bg-gray-stripes` : ``)"
        class="order-6"
      >
        <template #dropdown-button>
          <span class="hide-lg">Filter</span>
          <Icon name="ri:filter-2-line" class="show-lg -mb-0.5" />
        </template>

        <template v-if="hasFilters">
          <button @click="clearAllFilters">
            <div class="flex flex-row gap-1 items-center">
              <Icon name="ri:close-large-fill" />
              Clear All Filters
            </div>
          </button>
          <hr />
        </template>

        <div class="italic">Tag:</div>
        <MtDropdownCheckbox
          v-for="tag in taglist.data?.entries"
          :key="tag.entry"
          v-model="prefs.filters.tags[tag.entry]"
          :label="tag.entry"
        />
        <Icon v-if="taglist.status === 'pending'" name="svg-spinners:3-dots-fade" />

        <hr />

        <div class="italic">Author:</div>
        <input
          v-model="filterAuthorSearch"
          type="search"
          placeholder="Name..."
          autocomplete="off"
          @click="(ev) => ev.stopPropagation()"
        />
        <MtDropdownCheckbox
          v-for="author in authors"
          :key="author.entry"
          v-model="prefs.filters.authors[author.entry]"
          :label="author.entry"
        />
      </MtDropdown>
      <MtDropdown button-class="btn-gray" class="order-8">
        <template #dropdown-button>
          <span class="hide-lg">Columns</span>
          <Icon name="ri:layout-column-line" class="show-lg -mb-0.5" />
        </template>
        <MtDropdownCheckbox
          v-for="column in allColumns"
          :key="column.name"
          v-model="column.active"
          :label="column.title"
        />
      </MtDropdown>
      <MtDropdown button-class="btn-gray" class="order-9">
        <template #dropdown-button>
          <div class="flex flex-row gap-1 items-center">
            <span class="hide-lg">Sort:</span>
            <span>{{ prefs.sortBy }}</span>
            <Icon :name="prefs.sortAsc ? 'ri:sort-asc' : 'ri:sort-desc'" />
          </div>
        </template>

        <div class="italic">Sort by ...</div>
        <MtDropdownRadioGroup
          v-model="prefs.sortBy"
          :choices="['Title', 'Author', 'Tag', 'Date Uploaded', 'CCLI Number']"
        />

        <hr />

        <button @click="prefs.sortAsc = true">
          <Icon name="ri:sort-asc" />
          Ascending
        </button>
        <button @click="prefs.sortAsc = false">
          <Icon name="ri:sort-desc" />
          Descending
        </button>
      </MtDropdown>
      <div class="order-10">
        <NuxtLink class="inline-block btn-gray mr-2" to="/songs/search">
          <span class="hide-lg mr-1">Search</span>
          <Icon name="ri:search-line" class="-mb-0.5" />
        </NuxtLink>
        <NuxtLink v-if="canEdit" class="inline-block btn-blue" to="/songs/new">
          New...
        </NuxtLink>
      </div>
    </div>

    <MtTable
      :columns="columns"
      :data="sorted(filtered(songlist.data?.songs))"
      :error="songlist.isError"
      :row-click="async (row) => await navigateTo(`/songs/${row.id}`)"
    >
      <template #uploaded="{ row }">
        <Created :data="row" />
      </template>
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
      <template #tags="{ row }">
        <span v-for="tag in row.tags" :key="tag" class="spn-tag">{{ tag }}</span>
      </template>
      <template #ccli="{ row }">
        {{ row.ccli_num }}
      </template>
      <template #sparkline="{ row }">
        <MtSparkline v-if="sparklines.data" :data="sparklines.data.songs[row.id]" />
      </template>
      <template #versions="{ row }">
        <span
          v-for="version in versionlist.get({ songId: row.id }).data.value
            ?.song_versions"
          :key="version.id"
          class="spn-tag"
        >
          {{ version.label }}
        </span>
      </template>
    </MtTable>
  </div>
</template>

<script setup lang="ts">
import type { TableColumn } from "@/types/mt"
import type { Song, Entry } from "@/services/api"

import { useSonglistStore, useSongVersionlistStore } from "@/stores/songs"
import { useAuthorlistStore, useTaglistStore } from "@/stores/info"
import { useSonglistPrefsStore } from "@/stores/prefs"
import { useHistorySparklineStore } from "@/stores/history"
import { trimArray } from "@/utils"

const songlist = useSonglistStore()
const versionlist = useSongVersionlistStore()
const authorlist = useAuthorlistStore()
const taglist = useTaglistStore()

const prefs = useSonglistPrefsStore()
const sparklines = useHistorySparklineStore()

const { canEdit } = useRole()

const allColumns = ref([
  {
    name: "uploaded",
    title: "Uploaded",
    active: prefs.columns.uploaded ?? window.innerWidth > 800,
  },
  { name: "title", title: "Title", active: prefs.columns.title ?? true },
  { name: "authors", title: "Authors", active: prefs.columns.authors ?? true },
  {
    name: "tags",
    title: "Tags",
    active: prefs.columns.tags ?? window.innerWidth > 440,
  },
  { name: "ccli", title: "CCLI Number", active: prefs.columns.ccli ?? false },
  {
    name: "sparkline",
    title: "History (2 yr)",
    active: prefs.columns.sparkline ?? false,
  },
  { name: "versions", title: "Versions", active: prefs.columns.versions ?? false },
])

const columns = computed(() => allColumns.value.filter((c) => c.active))

watch(
  allColumns,
  (newV) => {
    prefs.columns = Object.fromEntries(newV.map((col) => [col.name, col.active]))
  },
  { deep: true },
)

const filterAuthorSearch = ref<string>()

const authors = computed<Entry[]>(() => {
  if (!authorlist.data?.entries) return []

  if (!filterAuthorSearch.value) {
    return authorlist.data.entries.filter((e) => prefs.filters.authors[e.entry])
  }

  const authorRe = new RegExp(filterAuthorSearch.value, "i")
  return authorlist.data.entries.filter(
    (e) => e.entry.match(authorRe) || prefs.filters.authors[e.entry],
  )
})

const hasFilters = computed(() => {
  if (Object.entries(prefs.filters.tags).some(([k, v]) => v)) return true
  if (Object.entries(prefs.filters.authors).some(([k, v]) => v)) return true
  return false
})

function clearAllFilters() {
  for (const k in prefs.filters.tags) {
    prefs.filters.tags[k] = false
  }
  for (const k in prefs.filters.authors) {
    prefs.filters.authors[k] = false
  }
  prefs.filters.title = ""
}

function filtered(songs: Song[] | undefined): Song[] | undefined {
  if (songs === undefined) return undefined

  const titleRe = prefs.filters.title ? new RegExp(prefs.filters.title, "i") : null
  const tags = new Set(
    Object.entries(prefs.filters.tags)
      .filter(([k, v]) => v)
      .map(([k, v]) => k),
  )
  const authors = new Set(
    Object.entries(prefs.filters.authors)
      .filter(([k, v]) => v)
      .map(([k, v]) => k),
  )

  return songs.filter((song) => {
    if (titleRe && !song.title.match(titleRe)) return false
    const songTags = new Set(song.tags ?? [])
    if (tags.size && songTags.intersection(tags).size === 0) return false
    const songAuthors = new Set(song.authors)
    if (authors.size && songAuthors.intersection(authors).size === 0) return false
    return true
  })
}

const numSongs = computed<{ filtered: number; total: number } | undefined>(() => {
  if (!songlist.data) return undefined

  return {
    total: songlist.data.songs.length,
    filtered: filtered(songlist.data.songs)!.length,
  }
})

function compareArrays(
  a: string[],
  b: string[],
  compareFn = (i: string, j: string) => i.localeCompare(j),
): number {
  const all = Object.fromEntries(a.map((v) => [v, -1]))
  b.forEach((v) => {
    all[v] = (all[v] ?? 0) + 1
  })
  for (const v of Object.keys(all).toSorted(compareFn)) {
    if (all[v] !== 0 && all[v] !== undefined) return all[v]
  }
  return 0
}

function sorted(songs: Song[] | undefined): Song[] | undefined {
  if (songs === undefined) return undefined

  return songs.toSorted((a, b) => {
    let delta = 0
    switch (prefs.sortBy) {
      case "Title":
        delta = a.title.localeCompare(b.title)
        break
      case "Author":
        delta = compareArrays(a.authors, b.authors, (i, j) =>
          i.split(" ").pop()!.localeCompare(j.split(" ").pop()!),
        )
        break
      case "Tag":
        delta = compareArrays(a.tags ?? [], b.tags ?? [])
        break
      case "Date Uploaded":
        delta = a.created_on.localeCompare(b.created_on)
        break
      case "CCLI Number":
        delta = (a.ccli_num ?? 0) - (b.ccli_num ?? 0)
        break
    }
    if (!prefs.sortAsc) delta = -delta
    return delta
  })
}
</script>
