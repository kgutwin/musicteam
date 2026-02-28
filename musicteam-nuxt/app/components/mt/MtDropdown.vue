<template>
  <div class="relative" @click="(ev) => ev.stopPropagation()">
    <div
      v-if="show"
      class="fixed top-0 left-0 w-screen h-screen z-10"
      @click="show = false"
    ></div>
    <div
      v-if="show"
      class="dropdown-menu"
      :class="leftward ? 'left-0' : 'right-0'"
      @click="show = false"
    >
      <slot />
    </div>
    <button
      ref="drop-button"
      type="button"
      :class="buttonClass"
      @click="show = true"
      :title="title"
      :disabled="disabled"
      data-cy="drop"
    >
      <slot name="dropdown-button">
        <Icon name="ri:arrow-down-s-line" />
      </slot>
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string
  buttonClass?: string
  disabled?: boolean
}>()
const show = ref(false)
const dropButton = useTemplateRef("drop-button")

const leftward = computed(() => {
  if (dropButton.value) {
    const pos = dropButton.value.getBoundingClientRect()
    return pos.right / window.innerWidth < 0.5
  }
  return false
})
</script>

<style>
.dropdown-menu {
  @apply absolute top-full z-20 w-40 text-sm rounded-lg bg-white p-2 border shadow-lg;
}
.dropdown-menu hr {
  @apply border-slate-500 m-2;
}
.dropdown-menu button,
.dropdown-menu label,
.dropdown-menu a {
  @apply block w-full text-left pl-1 py-0.5 rounded-lg hover:bg-slate-100 hover:shadow;
}
.dropdown-menu button:disabled,
.dropdown-menu label:disabled {
  @apply text-gray-500 hover:bg-slate-50 hover:shadow-none;
}
.dropdown-menu input[type=~"search"] {
  @apply w-full border rounded p-0.5;
}
.dropdown-menu ul li {
  @apply list-disc ml-4;
}
</style>
