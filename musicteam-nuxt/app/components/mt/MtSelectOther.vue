<template>
  <select v-model="choice" class="sel-dropdown" :disabled="disabled">
    <option v-for="opt in options" :key="opt">{{ opt }}</option>
    <option>Other...</option>
  </select>
  <input
    v-if="selectedOther || isOther"
    v-model="model"
    class="inp-text"
    :disabled="disabled"
  />
</template>

<script setup lang="ts">
import { ref, computed, watchEffect } from "vue"

const props = defineProps<{
  options: string[]
  disabled?: boolean
}>()

const model = defineModel<string | undefined>()

const selectedOther = ref(false)

const isOther = computed(() => model.value && !props.options.includes(model.value))
const choice = computed({
  get() {
    if (props.options.includes(model.value as string)) return model.value
    return model.value !== undefined ? "Other..." : undefined
  },
  set(newV) {
    if (newV === "Other...") {
      selectedOther.value = true
      model.value = undefined
    } else {
      selectedOther.value = false
      model.value = newV
    }
  },
})
</script>
