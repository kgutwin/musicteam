<template>
  <div>
    <div class="flex flex-row">
      <h1 class="grow">Songs</h1>
      <div>
        <NuxtLink class="btn-gray" to="/songs/new">New...</NuxtLink>
      </div>
    </div>
    <MtTable :columns="columns" :data="songs.data?.songs ?? []">
      <template #title="{ row }">
        <NuxtLink :to="`/songs/${row.id}`">{{ row.title }}</NuxtLink>
      </template>
      <template #authors="{ row }">
        <span v-for="author in row.authors" :key="author" class="author">
          {{ author }}
        </span>
      </template>
      <template #tags="{ row }">
        <span v-for="tag in row.tags" :key="tag" class="tag">{{ tag }}</span>
      </template>
      <template #created-on="{ row }">
        {{ row.created_on }}
      </template>
      <template #uploader="{ row }">
        {{ row.creator_id }}
      </template>
    </MtTable>
  </div>
</template>

<script setup lang="ts">
import { useSongsStore } from "@/stores/songs"
import type { TableColumn } from "@/types/mt"

const songs = useSongsStore()

const columns: TableColumn[] = [
  { name: "title", title: "Title" },
  { name: "authors", title: "Authors" },
  { name: "tags", title: "Tags" },
  { name: "created-on", title: "Uploaded On" },
  { name: "uploader", title: "Uploaded By" },
]
</script>
