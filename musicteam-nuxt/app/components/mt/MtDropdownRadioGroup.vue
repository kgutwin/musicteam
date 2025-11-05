<template>
  <label
    v-for="choice in choices"
    :key="choice"
    @click="(ev) => ev.stopPropagation()"
    class="flex flex-row items-baseline gap-1"
  >
    <input v-model="model" type="radio" :value="choice" />
    <div class="grow">{{ choice }}</div>
  </label>
</template>

<script setup lang="ts">
defineProps<{ choices: string[] }>()
const model = defineModel<string>()
</script>
