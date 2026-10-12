<template>
  <div class="div-panel">
    <div class="div-panel-tab-head">
      <div
        v-for="section in cols"
        :key="section"
        :class="{ grow: !open || open === section }"
        @click="open = open === section ? false : section"
      >
        <Icon
          name="ri:triangle-fill"
          class="icon-triangle"
          :class="{ open: open === section }"
        />
        <slot :name="`${section}-head`" />
      </div>
    </div>
    <div v-if="open">
      <slot :name="open" />
    </div>
  </div>
</template>

<script setup lang="ts">
// note: currently assumes two columns. Three or four should be fine
// as long as we have the right styles for it.
defineProps<{ cols: [string, string] }>()

const open = ref<false | string>(false)
</script>

<style>
.div-panel-tab-head {
  @apply flex flex-col sm:flex-row sm:gap-4;

  & > div {
    @apply flex flex-row gap-2 transition-all;
  }

  & > :not(:first-child) {
    @apply sm:border-l border-black sm:pl-4;
  }

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
.div-panel-tab-head:hover .icon-triangle {
  @apply visible;
}
</style>
