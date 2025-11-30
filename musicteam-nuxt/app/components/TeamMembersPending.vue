<template>
  <NuxtLink
    to="/team"
    v-if="pending"
    class="btn-users-pending"
    title="One or more users need to have a role assigned"
  >
    <Icon name="ri:account-circle-fill" size="40" class="text-white" />
  </NuxtLink>
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
  @apply self-end drop-shadow-[1px_1px_red];
}
</style>
