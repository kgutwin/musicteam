<template>
  <div class="recording-mark" :class="{ music: mark.song_version_id }">
    <div class="" @click="emit('play')">
      <Icon name="solar:tag-horizontal-outline" />
    </div>
    <div class="font-mono" @click="emit('play')">{{ timeString(mark.offset_sec) }}</div>
    <div v-if="position" class="grow font-bold" @click="emit('play')">
      {{ position.label }}
    </div>
    <MtEditable
      :class="{ grow: !position }"
      :model="mark"
      prop="cue_title"
      @save="saveMark('cue_title')"
    />
    <SetlistSidebarSong
      v-if="setlistSheet"
      read-only
      :sheet="setlistSheet"
      class="grow"
    />
    <button v-if="canEdit" class="hover:text-red-500" @click="deleteMark">
      <Icon name="solar:trash-bin-minimalistic-outline" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"
import { useSetlistPositionStore, useSetlistRefreshStore } from "@/stores/setlists"
import { timeString } from "@/utils"

import type { SetlistRecordingMark } from "@/services/api"

const props = defineProps<{
  setlistId: string
  mark: SetlistRecordingMark
}>()

const emit = defineEmits<{ play: [] }>()

const { canEdit } = useRole()

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

async function deleteMark() {
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
// - add edit/'nudge' buttons on the mark time
// - add marks to waveform view
// - add titles to icon buttons
// - add non-setlist sheet hyperlink here
// - try to get the waveform to scroll
// - figure out why it takes two clicks to focus the waveform view
// - comments on recordings ...
// - then... add player to song media listing
</script>

<style>
.recording-mark {
  @apply border shadow rounded bg-slate-50 px-2 py-1 my-2;
  @apply flex flex-row gap-2 items-baseline;
  @apply hover:bg-white cursor-pointer;
}
.recording-mark.music {
  @apply border-2 border-blue-200 bg-blue-50;
}
</style>
