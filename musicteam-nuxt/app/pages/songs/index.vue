<template>
  <div>
    <div class="flex flex-row">
      <h1 class="grow">Songs</h1>
      <div>
        <NuxtLink class="btn-gray" to="/songs/new">New...</NuxtLink>
      </div>
    </div>
    <MtTable
      :columns="columns"
      :data="songlist.data?.songs"
      :row-click="async (row) => await navigateTo(`/songs/${row.id}`)"
    >
      <template #uploaded="{ row }">
        {{ localdate(row.created_on) }} &centerdot;
        {{ initials(user.get({ userId: row.creator_id })?.data?.value?.name) }}
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
      <template #controls="{ row }">
        <!-- how to pick version and sheet from here?
        <MtDropdown>
          <button :disabled="!activeSetlistStore.setlist">
            <Icon name="ri:add-large-line" />
            Add to Candidates
          </button>
        </MtDropdown>
        -->
      </template>
    </MtTable>
  </div>
</template>

<script setup lang="ts">
import type { TableColumn } from "@/types/mt"

import { useSonglistStore } from "@/stores/songs"
import { useUserStore } from "@/stores/users"
import { trimArray, localdate } from "@/utils"

const songlist = useSonglistStore()
const user = useUserStore()
// const activeSetlistStore = useActiveSetlistStore()

const columns: TableColumn[] = [
  { name: "uploaded", title: "Uploaded" },
  { name: "title", title: "Title" },
  { name: "authors", title: "Authors" },
  { name: "tags", title: "Tags" },
  { name: "controls", title: "" },
]

function initials(name?: string) {
  if (!name) return ""
  return name.replace(/(.)(\S*\s*)/g, "$1")
}
</script>
