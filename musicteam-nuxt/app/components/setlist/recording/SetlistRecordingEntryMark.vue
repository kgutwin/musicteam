<template>
  <div class="recording-mark group" :class="{ music: mark.song_version_id }">
    <button class="recording-mark-timestamp" @click="emit('play')">
      <Icon name="solar:tag-horizontal-outline" />
      {{ timeString(mark.offset_sec) }}
    </button>
    <div v-if="canEdit" class="recording-mark-nudge-buttons group-hover:visible">
      <button @click="nudge('up')">
        <Icon name="solar:square-alt-arrow-up-outline" />
      </button>
      <button @click="nudge('down')">
        <Icon name="solar:square-alt-arrow-down-outline" />
      </button>
    </div>
    <button v-if="position" class="recording-mark-position-label" @click="emit('play')">
      {{ position.label }}
    </button>
    <MtEditable
      class="recording-mark-cue-title"
      :class="{ 'only-title': !position }"
      :model="mark"
      prop="cue_title"
      :placeholder="position ? '' : 'cue title'"
      @click="emit('play')"
      @save="saveMark('cue_title')"
    />
    <SetlistSidebarSong
      v-if="setlistSheet"
      read-only
      :sheet="setlistSheet"
      class="recording-mark-sidebar-song"
    />
    <div v-else-if="mark.song_id" class="recording-mark-song">
      <NuxtLink :to="`/songs/${mark.song_id}`" class="hover:underline">
        <Icon name="solar:music-note-4-outline" />
        {{ songs.get({ songId: mark.song_id }).data.value?.title }}
      </NuxtLink>
    </div>
    <button
      v-if="canEdit"
      class="recording-mark-delete invisible group-hover:visible"
      @click="deleteMark"
    >
      <Icon name="solar:trash-bin-minimalistic-outline" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"
import { useSongStore } from "@/stores/songs"
import { useSetlistPositionStore, useSetlistRefreshStore } from "@/stores/setlists"
import { timeString } from "@/utils"

import type { SetlistRecordingMark } from "@/services/api"

const props = defineProps<{
  setlistId: string
  mark: SetlistRecordingMark
}>()

const emit = defineEmits<{ play: [] }>()

const { canEdit } = useRole()

const songs = useSongStore()
const slist = useSetlistSheetlistStore().get({ setlistId: props.setlistId }).data
const refreshStore = useSetlistRefreshStore()

async function saveMark(field: keyof SetlistRecordingMark) {
  await api.setlists.updateSetlistRecordingMark(
    props.setlistId,
    props.mark.recording_id,
    props.mark.id,
    { [field]: props.mark[field] },
  )
  await refreshStore.refresh({
    setlistId: props.setlistId,
    recordingId: props.mark.recording_id,
  })
}

const position = computed(() => {
  if (!props.mark.setlist_position_id) return undefined

  return useSetlistPositionStore().get({
    setlistId: props.setlistId,
    positionId: props.mark.setlist_position_id,
  }).data.value
})

// This one's a little weird. The recording mark doesn't store a reference to the
// setlist sheet -- intentionally, because the recording mark cares about aligning
// to the actual song that was played, more so than whatever is in the setlist.
// Therefore, we *infer* the setlist sheet here, if we can; otherwise, we will
// show a more bare-bones link to the song version.
const setlistSheet = computed(() => {
  if (!props.mark.song_version_id) return undefined

  return (slist.value?.sheets ?? []).find(
    (s) =>
      s.setlist_position_id === props.mark.setlist_position_id &&
      s.song_version_id === props.mark.song_version_id,
  )
})

async function nudge(direction: "up" | "down") {
  await api.setlists.updateSetlistRecordingMark(
    props.setlistId,
    props.mark.recording_id,
    props.mark.id,
    { offset_sec: Math.max(0, props.mark.offset_sec + (direction === "up" ? 1 : -1)) },
  )
  await refreshStore.refresh({
    setlistId: props.setlistId,
    recordingId: props.mark.recording_id,
  })
}

async function deleteMark() {
  if (!window.confirm("Are you sure you want to delete this mark?")) return

  await useToaster(async () => {
    await api.setlists.deleteSetlistRecordingMark(
      props.setlistId,
      props.mark.recording_id,
      props.mark.id,
    )
    await refreshStore.refresh({
      setlistId: props.setlistId,
      recordingId: props.mark.recording_id,
    })
  })
}

// todo
// - comments on recordings ...
// - then... add player to song media listing
</script>

<style>
.recording-mark {
  @apply border shadow rounded bg-blue-100 px-2 py-1 my-2;
  @apply flex flex-row gap-x-0.5 sm:gap-x-2 items-baseline;
  @apply hover:bg-white;
  @apply flex-wrap md:flex-nowrap;

  & .mt-text-placeholder {
    @apply text-slate-400;
  }
  & .mt-text-placeholder:empty {
    @apply max-sm:!w-1;
  }
}
.recording-mark.music {
  @apply border-2 border-green-600 bg-green-100 hover:bg-white;
}
.recording-mark-timestamp {
  @apply order-1 leading-[0.5] font-mono py-2;
  @apply text-xs sm:text-sm md:text-base;
}
.recording-mark-nudge-buttons {
  @apply order-2 self-center hidden sm:flex flex-col leading-[0.5] invisible;
}
.recording-mark-position-label {
  @apply order-3 grow text-left font-bold ml-1;
}
.recording-mark-cue-title {
  @apply order-4 cursor-pointer mb-1;
}
.recording-mark-cue-title.only-title {
  @apply ml-1 grow;
}
.recording-mark-cue-title:not(.only-title):has(
    .editable-text:not(.mt-text-placeholder)
  ) {
  @apply order-6 basis-full sm:basis-auto;
}
.recording-mark-sidebar-song {
  @apply order-7 sm:order-6 grow;
}
.recording-mark-song {
  @apply order-8 sm:order-7 grow rounded-lg bg-white p-2;
}
.recording-mark-delete {
  @apply order-5 sm:order-8 hover:text-red-500;
}
</style>
