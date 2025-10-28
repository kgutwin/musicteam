<template>
  <div class="relative">
    <div
      v-if="show"
      class="fixed top-0 left-0 w-screen h-screen z-10"
      @click="show = false"
    ></div>
    <div v-if="show" class="dropdown-menu" @click="show = false">
      <slot />
    </div>
    <button type="button" @click="show = !show">
      <Icon name="ri:arrow-down-s-line" />
    </button>
  </div>
</template>

<script setup lang="ts">
const show = ref(false)
</script>

<style>
.dropdown-menu {
  @apply absolute right-0 top-4 z-20 w-40 text-sm rounded-lg bg-white p-2 border shadow-lg;
}
</style>
