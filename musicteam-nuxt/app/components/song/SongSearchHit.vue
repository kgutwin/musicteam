<template>
  <div>
    <div class="flex flex-row gap-4">
      <h2 class="grow">{{ hit.song.title }}</h2>
      <h3>{{ hit.song.authors.join(", ") }}</h3>
      <div v-if="(hit.song.tags?.length ?? 0) > 0">
        <span v-for="tag in hit.song.tags" :key="tag" class="spn-tag">{{ tag }}</span>
      </div>
    </div>
    <HighlightText :text="hit.highlighted" />
  </div>
</template>

<script setup lang="ts">
import type { SearchSongHit } from "@/services/api"

defineProps<{ hit: SearchSongHit }>()
</script>
