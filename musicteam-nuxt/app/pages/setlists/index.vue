<template>
  <div>
    <Head><Title>Set Lists - MusicTeam</Title></Head>

    <div class="flex flex-row">
      <h1 class="grow">Set Lists</h1>
      <div v-if="canLead">
        <NuxtLink class="btn-gray" to="/setlists/new">New...</NuxtLink>
      </div>
    </div>

    <MtTable
      :columns="columns"
      :data="setlists.data?.setlists"
      :error="setlists.isError"
      :row-click="async (row) => await navigateTo(`/setlists/${row.id}`)"
    >
      <template #service-date="{ row }">
        <NuxtLink :to="`/setlists/${row.id}`" class="hover:underline">
          {{ localdate(row.service_date) }}
        </NuxtLink>
      </template>
      <template #leader="{ row }">
        {{ row.leader_name }}
      </template>
      <template #title="{ row }">
        {{ row.title }}
      </template>
      <template #team="{ row }">
        <span v-for="name in row.participants" :key="name" class="spn-tag">
          {{ name }}
        </span>
      </template>
      <template #tags="{ row }">
        <span v-for="tag in row.tags" :key="tag" class="spn-tag">{{ tag }}</span>
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

const { canLead } = useRole()

const allColumns: TableColumn[] = [
  { name: "service-date", title: "Service Date" },
  { name: "leader", title: "Leader" },
  { name: "title", title: "Title", active: window.innerWidth > 400 },
  { name: "team", title: "Participants" },
  { name: "tags", title: "Tags", active: window.innerWidth > 800 },
]

const columns = computed(() => allColumns.filter((c) => c.active ?? true))
</script>
