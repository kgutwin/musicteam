<template>
  <label
    v-for="opt in opts"
    :key="opt.choice"
    @click="(ev) => ev.stopPropagation()"
    class="menu-lbl-radio"
  >
    <input v-model="model" type="radio" :value="opt.choice" />
    <div class="grow">{{ opt.label }}</div>
  </label>
</template>

<script setup lang="ts">
const props = defineProps<{ choices: string[] | Record<string, string> }>()
const model = defineModel<string>()

const opts = computed(() =>
  Array.isArray(props.choices)
    ? props.choices.map((c) => ({ choice: c, label: c }))
    : Object.entries(props.choices).map(([choice, label]) => ({ choice, label })),
)
</script>

<style>
.dropdown-menu label.menu-lbl-radio {
  @apply flex flex-row items-baseline gap-1;
}
</style>
