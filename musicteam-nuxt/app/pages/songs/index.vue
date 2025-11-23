<template>
  <div>
    <Head><Title>Songs - MusicTeam</Title></Head>
    <div class="flex flex-row items-baseline gap-2 flex-wrap sm:flex-nowrap">
      <h1 class="grow hide-sm">Songs</h1>
      <div v-if="numSongs" class="hide-lg">
        <template v-if="numSongs.filtered !== numSongs.total">
          {{ numSongs.filtered }} of
        </template>
        {{ numSongs.total }} songs
      </div>
      <div>
        <input
          v-model="filterTitle"
          type="search"
          placeholder="Filter by Title..."
          class="inp-text w-32 md:w-48"
        />
      </div>
      <MtDropdown button-class="btn-gray">
        <template #dropdown-button>
          <Icon name="ri:filter-2-line" class="show-lg" />
          <span class="hide-lg">Filter</span>
        </template>

        <div class="italic">Tag:</div>
        <MtDropdownCheckbox
          v-for="tag in taglist.data?.entries"
          :key="tag.entry"
          v-model="filterTags[tag.entry]"
          :label="tag.entry"
        />

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
          v-model="filterAuthors[author.entry]"
          :label="author.entry"
        />
      </MtDropdown>
      <MtDropdown button-class="btn-gray">
        <template #dropdown-button>
          <Icon name="ri:layout-column-line" class="show-lg" />
          <span class="hide-lg">Columns</span>
        </template>
        <MtDropdownCheckbox
          v-for="column in allColumns"
          :key="column.name"
          v-model="column.active"
          :label="column.title"
        />
      </MtDropdown>
      <MtDropdown button-class="btn-gray">
        <template #dropdown-button>
          <span class="hide-lg">Sort:</span>
          {{ sortBy }}
          <Icon :name="sortAsc ? 'ri:sort-asc' : 'ri:sort-desc'" />
        </template>

        <div class="italic">Sort by ...</div>
        <MtDropdownRadioGroup
          v-model="sortBy"
          :choices="['Title', 'Author', 'Tag', 'Date Uploaded', 'CCLI Number']"
        />

        <hr />

        <button @click="sortAsc = true">
          <Icon name="ri:sort-asc" />
          Ascending
        </button>
        <button @click="sortAsc = false">
          <Icon name="ri:sort-desc" />
          Descending
        </button>
      </MtDropdown>
      <div>
        <NuxtLink class="inline-block btn-blue" to="/songs/new">New...</NuxtLink>
      </div>
    </div>
    <MtTable
      :columns="columns"
      :data="sorted(filtered(songlist.data?.songs))"
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
import { trimArray } from "@/utils"

const songlist = useSonglistStore()
const versionlist = useSongVersionlistStore()
const authorlist = useAuthorlistStore()
const taglist = useTaglistStore()

const allColumns = ref([
  { name: "uploaded", title: "Uploaded", active: window.innerWidth > 800 },
  { name: "title", title: "Title", active: true },
  { name: "authors", title: "Authors", active: true },
  { name: "tags", title: "Tags", active: window.innerWidth > 400 },
  { name: "ccli", title: "CCLI Number", active: false },
  { name: "versions", title: "Versions", active: false },
])

const columns = computed(() => allColumns.value.filter((c) => c.active))

const filterTitle = ref<string>()
const filterTags = ref<Record<string, boolean>>({})
const filterAuthors = ref<Record<string, boolean>>({})
const filterAuthorSearch = ref<string>()

const authors = computed<Entry[]>(() => {
  if (!authorlist.data?.entries) return []

  if (!filterAuthorSearch.value) {
    return authorlist.data.entries.filter((e) => filterAuthors.value[e.entry])
  }

  const authorRe = new RegExp(filterAuthorSearch.value, "i")
  return authorlist.data.entries.filter(
    (e) => e.entry.match(authorRe) || filterAuthors.value[e.entry],
  )
})

function filtered(songs: Song[] | undefined): Song[] | undefined {
  if (songs === undefined) return undefined

  const titleRe = filterTitle.value ? new RegExp(filterTitle.value, "i") : null
  const tags = new Set(
    Object.entries(filterTags.value)
      .filter(([k, v]) => v)
      .map(([k, v]) => k),
  )
  const authors = new Set(
    Object.entries(filterAuthors.value)
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

const sortBy = ref<"Title" | "Author" | "Tag" | "Date Uploaded" | "CCLI Number">(
  "Title",
)
const sortAsc = ref(true)

function sorted(songs: Song[] | undefined): Song[] | undefined {
  if (songs === undefined) return undefined

  return songs.toSorted((a, b) => {
    let delta = 0
    switch (sortBy.value) {
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
    if (!sortAsc.value) delta = -delta
    return delta
  })
}
</script>
