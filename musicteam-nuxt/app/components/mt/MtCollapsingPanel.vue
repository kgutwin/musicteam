<template>
  <div class="div-panel div-panel-cols-2">
    <div v-for="section in cols" :key="section">
      <div class="div-panel-sub-head" @click="open = !open">
        <Icon name="ri:triangle-fill" class="icon-triangle" :class="{ open }" />
        <slot :name="`${section}-head`" />
      </div>
      <slot v-if="open" :name="section" />
    </div>
  </div>
</template>

<script setup lang="ts">
// note: currently assumes two columns. Three or four should be fine
// as long as we have the right styles for it.
defineProps<{ cols: [string, string] }>()

const open = ref(false)
</script>

<style>
.div-panel-cols-2 {
  @apply grid grid-cols-1 sm:grid-cols-2 gap-4;

  & > :not(:first-child) {
    @apply sm:border-l border-black sm:pl-4;
  }
}

.div-panel-sub-head {
  @apply flex flex-row items-center gap-1 cursor-pointer;

  & .icon-triangle {
    @apply self-center text-sm transition;
  }
  & .icon-triangle.open {
    @apply rotate-180 visible;
  }
  & .icon-triangle:not(.open) {
    @apply rotate-90 invisible;
  }

  & label {
    @apply block font-bold cursor-pointer grow;
  }
}
.div-panel-sub-head:hover .icon-triangle {
  @apply visible;
}
</style>
