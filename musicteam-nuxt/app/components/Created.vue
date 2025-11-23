<template>
  <span>
    {{ localdate(data.created_on) }} &centerdot;
    {{ initials(user.get({ userId: data.creator_id })?.data?.value?.name) }}
  </span>
</template>

<script setup lang="ts">
import { localdate } from "@/utils"
import { useUserStore } from "@/stores/users"

defineProps<{ data: { created_on: string; creator_id: string } }>()

const user = useUserStore()

function initials(name?: string) {
  if (!name) return ""
  return name.replace(/(.)(\S*\s*)/g, "$1")
}
</script>
