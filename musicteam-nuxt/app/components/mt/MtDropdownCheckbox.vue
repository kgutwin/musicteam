<template>
  <label
    @click="(ev) => ev.stopPropagation()"
    :disabled="disabled"
    class="menu-lbl-checkbox"
  >
    <input v-model="model" type="checkbox" :disabled="disabled" />
    <div class="grow">{{ label }}</div>
  </label>
</template>

<script setup lang="ts">
defineProps<{ label: string; disabled?: boolean }>()
const model = defineModel<boolean>()
</script>

<style>
.dropdown-menu label.menu-lbl-checkbox {
  @apply flex flex-row items-baseline gap-1;
}
</style>
