<template>
  <span
    v-if="pending > 0"
    class="btn-users-pending"
    title="One or more users need to have a role assigned"
    >{{ pending }}</span
  >
</template>

<script setup lang="ts">
import { useUserlistStore } from "@/stores/users"

const users = useUserlistStore()

const pending = computed(
  () => (users.data?.users ?? []).filter((u) => u.role === "pending").length,
)
</script>

<style>
.btn-users-pending {
  @apply inline-block text-xs px-1.5 align-top rounded-full bg-red-500 text-white;
}
</style>
