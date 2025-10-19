<template>
  <div>
    <h2>Songs</h2>
    <div>Response: {{ response.data }}</div>
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"

const response = await api.names.names("foo", { count: 5 })
console.log(response)
</script>
