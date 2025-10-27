<template>
  <div>
    <h1>Team Members</h1>
    <MtTable :columns="columns" :data="users.data?.users ?? []">
      <template #picture="{ row }">
        <img
          :src="row.picture"
          class="h-8 w-8 rounded-full mx-auto"
          referrerpolicy="no-referrer"
        />
      </template>
      <template #name="{ row }">
        {{ row.name }}
      </template>
      <template #email="{ row }">
        {{ row.email }}
      </template>
      <template #role="{ row }">
        {{ row.role }}
      </template>
    </MtTable>
  </div>
</template>

<script setup lang="ts">
import { useUserlistStore } from "@/stores/users"
import type { TableColumn } from "@/types/mt"

const users = useUserlistStore()

const columns: TableColumn[] = [
  { name: "picture", title: "" },
  { name: "name", title: "Name" },
  { name: "email", title: "Email" },
  { name: "role", title: "Role" },
]
</script>
