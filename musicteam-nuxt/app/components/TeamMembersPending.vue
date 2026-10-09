<template>
  <span
    v-if="pending"
    class="btn-users-pending"
    title="One or more users need to have a role assigned"
  >
    *
  </span>
</template>

<script setup lang="ts">
import { useUserlistStore } from "@/stores/users"

const users = useUserlistStore()

const pending = computed(() =>
  (users.data?.users ?? []).some((u) => u.role === "pending"),
)
</script>

<style>
.btn-users-pending {
  @apply self-end text-red-500;
}
</style>
