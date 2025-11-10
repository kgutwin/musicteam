<template>
  <div class="relative" @click="(ev) => ev.stopPropagation()">
    <div
      v-if="show"
      class="fixed top-0 left-0 w-screen h-screen z-10"
      @click="show = false"
    ></div>
    <div v-if="show" class="dropdown-menu" @click="show = false">
      <slot />
    </div>
    <button
      type="button"
      :class="buttonClass"
      @click="show = !show"
      :title="title"
      :disabled="disabled"
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
</script>

<style>
.dropdown-menu {
  @apply absolute right-0 top-full z-20 w-40 text-sm rounded-lg bg-white p-2 border shadow-lg;
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
