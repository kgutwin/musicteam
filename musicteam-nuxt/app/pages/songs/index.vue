<template>
  <div>
    <div class="flex flex-row">
      <h1 class="grow">Songs</h1>
      <div>
        <NuxtLink class="btn-gray" to="/songs/new">New...</NuxtLink>
      </div>
    </div>
    <MtTable :columns="columns" :data="songlist.data?.songs ?? []">
      <template #title="{ row }">
        <NuxtLink :to="`/songs/${row.id}`" class="hover:underline">
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
      <template #created-on="{ row }">
        {{ localdate(row.created_on) }}
      </template>
      <template #uploader="{ row }">
        {{ user.get({ userId: row.creator_id })?.data?.value?.name }}
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

const columns: TableColumn[] = [
  { name: "title", title: "Title" },
  { name: "authors", title: "Authors" },
  { name: "tags", title: "Tags" },
  { name: "created-on", title: "Uploaded On" },
  { name: "uploader", title: "Uploaded By" },
]
</script>
