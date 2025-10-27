<template>
  <select v-model="choice" class="sel-dropdown" :disabled="disabled">
    <option v-for="opt in options" :key="opt">{{ opt }}</option>
    <option>Other...</option>
  </select>
  <input v-if="selectedOther" v-model="other" class="inp-text" :disabled="disabled" />
</template>

<script setup lang="ts">
const props = defineProps<{
  options: string[]
  disabled?: boolean
}>()

const model = defineModel<string | undefined>()

const other = ref<string | undefined>()
const selectedOther = ref(false)

const choice = computed({
  get() {
    if (props.options.includes(model.value as string)) return model.value
    return selectedOther.value ? "Other..." : undefined
  },
  set(newV) {
    selectedOther.value = newV === "Other..."
    model.value = newV === "Other..." ? other.value : newV
  },
})

watchEffect(() => {
  if (selectedOther.value) model.value = other.value
})
</script>
