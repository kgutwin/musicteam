<template>
  <div
    v-if="hits.length > 0"
    class="flex flex-row flex-wrap items-center gap-1 text-sky-600"
  >
    <Icon name="solar:info-circle-broken" class="text-sky-900" />
    In library:
    <div v-for="song in hits" class="text-sky-800">
      <NuxtLink :to="`/songs/${song.id}`" target="_new">
        {{ song.title }}
        <Icon name="solar:square-top-down-outline" size="0.8em" />
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"
import type { Song } from "@/services/api"

const props = defineProps<{ title?: string; ccliNum?: string }>()

const hits = ref<Song[]>([])
const debounce = ref<ReturnType<typeof setTimeout> | null>(null)

type Query = Parameters<typeof api.songs.listSongs>[0]

watch(
  props,
  () => {
    if (debounce.value) window.clearTimeout(debounce.value)

    let query: Query | null = null
    if (props.title && props.title.length > 2) {
      query = { title: props.title }
    } else if (props.ccliNum) {
      query = { ccli_num: parseInt(props.ccliNum) }
    }

    if (!query) {
      hits.value = []
      return
    }

    debounce.value = setTimeout(
      (q: Query) => {
        api.songs.listSongs(q).then((resp) => {
          hits.value = resp.data.songs
          debounce.value = null
        })
      },
      500,
      query,
    )
  },
  { immediate: true },
)
</script>
