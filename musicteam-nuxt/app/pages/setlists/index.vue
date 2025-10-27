<template>
  <div>
    <div class="flex flex-row">
      <h1 class="grow">Set Lists</h1>
      <div>
        <NuxtLink class="btn-gray" to="/setlists/new">New...</NuxtLink>
      </div>
    </div>

    <MtTable :columns="columns" :data="setlists.data?.setlists ?? []">
      <template #service-date="{ row }">
        <NuxtLink :to="`/setlists/${row.id}`" class="hover:underline">
          {{ row.service_date }}
        </NuxtLink>
      </template>
      <template #leader="{ row }">
        {{ row.leader_name }}
      </template>
      <template #tags="{ row }">
        <span v-for="tag in row.tags" :key="tag" class="spn-tag">{{ tag }}</span>
      </template>
      <template #created-on="{ row }">
        {{ localdate(row.created_on) }}
      </template>
      <template #created-by="{ row }">
        {{ user.get({ userId: row.creator_id })?.data?.value?.name }}
      </template>
    </MtTable>
  </div>
</template>

<script setup lang="ts">
import { useSetlistlistStore } from "@/stores/setlists"
import { useUserStore } from "@/stores/users"
import type { TableColumn } from "@/types/mt"

const setlists = useSetlistlistStore()
const user = useUserStore()

const columns: TableColumn[] = [
  { name: "service-date", title: "Service Date" },
  { name: "leader", title: "Leader" },
  { name: "tags", title: "Tags" },
  { name: "created-on", title: "Created On" },
  { name: "created-by", title: "Created By" },
]
</script>
