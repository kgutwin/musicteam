<template>
  <div v-if="setlistInfo.data" class="lyrics-base">
    <Head><Title>Lyrics - MusicTeam</Title></Head>
    <h1>
      <div class="text-size">
        <button class="text-base" @click="largeText = false">
          <Icon name="ri:font-size" />
        </button>
        <button @click="largeText = true">
          <Icon name="ri:font-size" />
        </button>
      </div>
      Songs for {{ localdate(setlistInfo.data.service_date, "short") }}
      <div v-if="setlistInfo.data.title" class="title">
        "{{ setlistInfo.data.title }}"
      </div>
    </h1>

    <div v-for="song in setlistInfo.data.lyrics" :key="song.position_id" class="song">
      <button
        class="song-title"
        @click="isOpen[song.position_id] = !isOpen[song.position_id]"
      >
        <Icon
          name="ri:triangle-fill"
          class="icon-triangle"
          :class="{ open: isOpen[song.position_id] }"
        />
        {{ song.title }}
      </button>
      <div
        v-if="isOpen[song.position_id]"
        class="lyrics"
        :class="{ 'text-xl': largeText }"
      >
        {{ trimTitle(song.title, song.lyrics) }}
        <button class="close-song" @click="isOpen[song.position_id] = false">
          <Icon name="ri:arrow-up-line" />
        </button>
      </div>
    </div>

    <div v-if="false">{{ setlistInfo.data }}</div>
  </div>
  <div v-else-if="setlistInfo.isError" class="lyrics-loading">
    <h1>Whoops!</h1>
    <h3>Something went wrong, sorry... let us know!</h3>
  </div>
  <div v-else class="lyrics-loading">
    <h1>Welcome!</h1>
    <h3>
      Hang on for a few moments while the lyrics load
      <Icon name="svg-spinners:3-dots-fade" />
    </h3>
  </div>
</template>

<script setup lang="ts">
import { useSetlistInfoLatestStore } from "@/stores/setlists"
import { localdate } from "@/utils"

declare module "nuxt/app" {
  interface NuxtLayouts {
    blank: unknown
  }
}
definePageMeta({
  auth: false,
  layout: "blank",
})

const setlistInfo = useSetlistInfoLatestStore()

const largeText = ref(false)
const isOpen = ref<Record<string, boolean>>({})

function trimTitle(title: string, lyrics: string | null) {
  if (!lyrics) return ""

  if (lyrics.startsWith(title)) {
    lyrics = lyrics.replace(title, "")
  }
  return lyrics.trim()
}
</script>

<style>
.lyrics-base {
  & h1 {
    @apply w-full px-4 py-2;
    @apply bg-gradient-to-tr from-blue-200 to-sky-100;

    & .title {
      @apply italic text-base font-light;
    }

    & .text-size {
      @apply float-right mt-1;
      @apply flex flex-row gap-1 items-center;
      @apply rounded-lg bg-gradient-to-tr from-slate-200 to-gray-100 px-1;
      @apply border border-slate-300 divide-x-2 divide-slate-300;
      @apply shadow;
      @apply text-gray-600;

      & button {
        @apply pt-1 px-2;
      }
    }
  }

  & .song {
    & .song-title {
      @apply block px-6 py-4 w-full text-left text-lg font-semibold;
      @apply bg-gradient-to-tr from-slate-200 to-gray-100;
      @apply border-b border-slate-300;

      & .icon-triangle {
        @apply text-xs transition text-slate-500;
      }
      & .icon-triangle.open {
        @apply rotate-180;
      }
      & .icon-triangle:not(.open) {
        @apply rotate-90;
      }
    }

    & .lyrics {
      @apply px-2 whitespace-pre-wrap pt-2 pb-8;
    }

    & .close-song {
      @apply rounded-full bg-blue-200 text-2xl size-12 float-right mr-2 mb-4 shadow-lg;
    }
  }
}

.lyrics-loading {
  @apply flex flex-col p-4 w-full h-screen items-center justify-center text-center gap-1;
}
</style>
