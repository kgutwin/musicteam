<template>
  <div class="recording-entry-panel">
    <div class="recording-player-row">
      <UserIcon :user-id="recording.creator_id" class="w-6" />
      <div class="text-sm">{{ localdate(recording.created_on) }}</div>
      <MtDropdown v-if="canEdit" class="self-end">
        <template #dropdown-button>
          <Icon name="solar:home-add-bold" class="text-slate-500 rotate-90" />
        </template>

        <i>Add Mark for...</i>
        <button v-for="position in markCandidates" @click="newMark(position)">
          <div :class="{ 'font-bold': position.is_music }">{{ position.label }}</div>
          <div v-if="position.songId">
            {{ songs.get({ songId: position.songId }).data.value?.title ?? "" }}
          </div>
        </button>
        <hr />
        <button @click="newMark()">Other</button>
      </MtDropdown>
      <audio
        ref="player"
        :src="url"
        controls
        class="w-full"
        @timeupdate="
          (ev) => {
            waveform.cursor = (ev.target as HTMLMediaElement).currentTime
            waveform.draw()
          }
        "
      />
      <button @click="download">
        <Icon name="solar:download-minimalistic-bold" />
      </button>
      <button v-if="canEdit" class="hover:text-red-500" @click="deleteEntry">
        <Icon name="solar:trash-bin-minimalistic-outline" />
      </button>
    </div>
    <div class="recording-scroller">
      <canvas
        ref="canvas"
        class="recording-waveform"
        width="1470"
        height="150"
        tabindex="1"
        @mousemove="canvasMouseEvent"
        @click="canvasMouseEvent"
        @keydown.prevent="canvasKeyEvent"
      >
        Recording waveform
      </canvas>
    </div>
    <div class="bookmark-list">
      <SetlistRecordingEntryMark
        v-for="mark in marks?.marks ?? []"
        :setlist-id="recording.setlist_id"
        :mark="mark"
        @play="playFrom(mark.offset_sec)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"
import { useSongStore } from "@/stores/songs"
import {
  useSetlistPositionlistStore,
  useSetlistSheetlistStore,
  useSetlistRecordingMarklistStore,
  useSetlistRefreshStore,
} from "@/stores/setlists"
import { localdate } from "@/utils"
import mime from "mime-types"
import { WaveformViewer } from "./waveform"

import type { SetlistRecording, SetlistPosition, Song } from "@/services/api"

const props = defineProps<{ recording: SetlistRecording }>()

const { canEdit } = useRole()

const songs = useSongStore()
const positions = useSetlistPositionlistStore().get({
  setlistId: props.recording.setlist_id,
}).data
const slist = useSetlistSheetlistStore().get({
  setlistId: props.recording.setlist_id,
}).data
const marks = useSetlistRecordingMarklistStore().get({
  setlistId: props.recording.setlist_id,
  recordingId: props.recording.id,
}).data
const refreshStore = useSetlistRefreshStore()

interface AnnotatedPosition extends SetlistPosition {
  songVersionId?: string
  songId?: string
}

const markCandidates = computed<AnnotatedPosition[]>(() => {
  if (!positions.value || !slist.value) return []

  return positions.value.positions.flatMap((p) => {
    if (!p.is_music) return [p]

    const songs = Object.fromEntries(
      (slist.value?.sheets ?? [])
        .filter((s) => s.setlist_position_id === p.id)
        .map((s) => [s.song_id, s.song_version_id]),
    )
    if (Object.keys(songs).length === 0) {
      return [p]
    } else {
      return Object.entries(songs).map(([songId, songVersionId]) => ({
        ...p,
        songVersionId,
        songId,
      }))
    }
  })
})

const url = computed(
  () =>
    `/api/setlists/${props.recording.setlist_id}/recordings/${props.recording.id}/audio`,
)

const canvas = useTemplateRef("canvas")
const player = useTemplateRef("player")
const waveform = new WaveformViewer(
  props.recording.duration,
  JSON.parse(props.recording.waveform ?? "[]"),
)
watchEffect(() => {
  if (canvas.value) {
    waveform.setCanvas(canvas.value)
  }
})

function canvasMouseEvent(ev: MouseEvent) {
  if (ev.type === "mousemove" && ev.buttons === 0) return
  if (player.value) {
    const pos =
      (ev.offsetX / (ev.target as HTMLCanvasElement).clientWidth) * waveform.duration
    player.value.currentTime = pos
  }
}

function canvasKeyEvent(ev: KeyboardEvent) {
  if (player.value) {
    if (ev.code === "Space") {
      if (player.value.paused) {
        player.value.play()
      } else {
        player.value.pause()
      }
    } else if (ev.code === "ArrowRight" || ev.code === "ArrowLeft") {
      const delta = ev.shiftKey ? 10 : 1
      player.value.currentTime += ev.code === "ArrowRight" ? delta : -delta
    } else {
      // console.log(ev.code)
    }
  }
}

async function newMark(position?: AnnotatedPosition) {
  if (waveform.cursor < 0) return

  await useToaster(async () => {
    await api.setlists.newSetlistRecordingMark(
      props.recording.setlist_id,
      props.recording.id,
      {
        offset_sec: waveform.cursor,
        setlist_position_id: position?.id ?? null,
        song_version_id: position?.songVersionId ?? null,
        cue_title: null,
      },
    )
    await refreshStore.refresh({
      setlistId: props.recording.setlist_id,
      recordingId: props.recording.id,
    })
  })
}

function playFrom(offset: number) {
  if (player.value) {
    player.value.currentTime = offset
    if (player.value.paused) {
      player.value.play()
    }
  }
}

async function deleteEntry() {
  if (!window.confirm("Are you sure you want to delete this recording?")) return

  await useToaster(async () => {
    await api.setlists.deleteSetlistRecording(
      props.recording.setlist_id,
      props.recording.id,
    )
    await refreshStore.refresh({ setlistId: props.recording.setlist_id })
  })
}

async function download() {
  let ext = mime.extension(props.recording.object_type)

  const link = document.createElement("a")
  link.href = url.value
  link.download = `recording.${ext}`

  // note: this doesn't seem to actually be causing a download; it opens in a new tab.
  // I'm guessing maybe it's because the url actually is a 302 to S3 and that causes
  // the content-disposition to get lost?
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

<style>
.recording-entry-panel {
  @apply p-8 rounded-lg border shadow-lg bg-slate-100;
}
.recording-player-row {
  @apply flex flex-row gap-2 items-center;

  & button {
    @apply self-end;
  }
  & button .iconify {
    @apply text-xl;
  }
}
.recording-scroller {
  @apply overflow-auto;
}
.recording-waveform {
  @apply mt-1 block border rounded; /* scale-x-150 origin-left; */
  image-rendering: pixelated;
  outline: none;
}
.bookmark-list {
  /* @apply flex flex-row gap-2 items-baseline mt-2; */
}
</style>
