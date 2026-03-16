<template>
  <div>
    <Head><Title>Team - MusicTeam</Title></Head>

    <h1>Team Members</h1>
    <MtTable :columns="columns" :data="users.data?.users" :error="users.isError">
      <template #picture="{ row }">
        <img
          v-if="row.picture"
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
        <MtEditable
          :model="row"
          prop="role"
          edit-needs="manager"
          @save="saveRole(row)"
          data-cy="role-editable"
        >
          <template #input="{ modelValue, updateModelValue }">
            <select
              :value="modelValue"
              @change="
                (ev) =>
                  updateModelValue((ev.target as HTMLSelectElement).value as UserRole)
              "
            >
              <option>viewer</option>
              <option>leader</option>
              <option>manager</option>
              <option v-if="canAdmin">admin</option>
              <option>inactive</option>
            </select>
          </template>
        </MtEditable>
        <span v-if="row.role === 'pending'" class="text-red-500">*</span>
      </template>
    </MtTable>
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"
import { useUserlistStore, useUserRefreshStore } from "@/stores/users"

import type { TableColumn } from "@/types/mt"
import type { User } from "@/services/api"

const users = useUserlistStore()
const refreshStore = useUserRefreshStore()
const { canAdmin } = useRole()

type UserRole = "viewer" | "leader" | "manager" | "admin" | "inactive"

const allColumns: TableColumn[] = [
  { name: "picture", title: "" },
  { name: "name", title: "Name" },
  { name: "email", title: "Email", active: window.innerWidth > 800 },
  { name: "role", title: "Role" },
]

const columns = computed(() => allColumns.filter((c) => c.active ?? true))

async function saveRole(row: User) {
  await useToaster(async () => {
    await api.users.updateUser(row.id, { role: row.role })
  })
  await refreshStore.refresh({ userId: row.id })
}
</script>
