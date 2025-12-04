<template>
  <div class="div-panel grid grid-cols-1 sm:grid-cols-2 gap-4">
    <div>
      <div class="div-panel-sub-head" @click="open = !open">
        <Icon name="ri:triangle-fill" class="icon-triangle" :class="{ open }" />
        <label>Comments</label>
        <CommentsIcons :resource-id="versionId" />
      </div>
      <CommentsPanel v-if="open" class="mt-1" :resource-id="versionId" />
    </div>
    <div class="sm:border-l border-black sm:pl-4">
      <div class="div-panel-sub-head" @click="open = !open">
        <Icon name="ri:triangle-fill" class="icon-triangle" :class="{ open }" />
        <label>Media</label>
      </div>
      <div v-if="open">Coming soon...</div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ versionId: string }>()

const open = ref(false)
</script>

<style>
.div-panel-sub-head {
  @apply flex flex-row items-baseline gap-1 cursor-pointer;

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
