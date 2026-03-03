<template>
  <PingBar v-if="pingStore.isPinging" />
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup lang="ts">
import { usePingStore } from "@/stores/ping"

const pingStore = usePingStore()
pingStore.ping()
</script>
