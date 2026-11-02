<template>
  <div class="recording-entry-panel">
    <div class="recording-player-row">
      <UserIcon :user-id="recording.creator_id" class="w-6" />
      <div class="text-sm">{{ localdate(recording.created_on) }}</div>
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
      <button @click="download" title="Download">
        <Icon name="solar:download-minimalistic-bold" />
      </button>
      <button
        v-if="canEdit"
        class="hover:text-red-500"
        title="Delete Recording"
        @click="deleteEntry"
      >
        <Icon name="solar:trash-bin-minimalistic-outline" />
      </button>
    </div>
    <div class="flex flex-row gap-2">
      <div v-if="canEdit" class="flex flex-col text-xl mr-1 pt-1">
        <button @click="zoom('in')" title="Zoom In">
          <Icon name="solar:magnifier-zoom-in-linear" />
        </button>
        <button @click="zoom('out')" title="Zoom Out">
          <Icon name="solar:magnifier-zoom-out-linear" />
        </button>
        <MtDropdown class="self-end" title="Add Mark at Cursor">
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
      </div>
      <div class="recording-scroller">
        <canvas
          ref="canvas"
          class="recording-waveform"
          :width="waveformWidth"
          height="150"
          tabindex="1"
          @mousemove="canvasMouseEvent"
          @click="canvasMouseEvent"
          @keydown.prevent="canvasKeyEvent"
        >
          Recording waveform
        </canvas>
        <div
          v-for="mark in waveformMarks"
          class="absolute w-8 h-8"
          :style="`top: 22px; left: ${Math.max(0, mark.offset - 8)}px`"
          :id="`mark-${mark.time}`"
        />
      </div>
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
const waveformWidth = ref(1470)
const waveform = new WaveformViewer(
  props.recording.duration,
  JSON.parse(props.recording.waveform ?? "[]"),
)
watchEffect(() => {
  if (canvas.value) {
    waveform.setCanvas(canvas.value)
  }
})

const waveformMarks = computed(() => {
  if (marks.value) {
    return marks.value.marks.map((m, i) => {
      let label = `${i + 1}`
      if (m.setlist_position_id) {
        const pos = useSetlistPositionStore().get({
          setlistId: props.recording.setlist_id,
          positionId: m.setlist_position_id,
        }).data.value
        if (pos) {
          label = pos.label
        }
      } else if (m.cue_title) {
        label = m.cue_title
      }

      return {
        time: m.offset_sec,
        offset: Math.round(
          (waveformWidth.value / props.recording.duration) * m.offset_sec,
        ),
        label,
        color: m.song_version_id
          ? "rgb(22 163 74)" // bg-green-600
          : "rgb(161 161 170)", // bg-zinc-400
      }
    })
  } else {
    return []
  }
})

watchEffect(() => {
  waveform.setMarks(waveformMarks.value)
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

function zoom(direction: "in" | "out") {
  if (direction === "in") {
    waveformWidth.value = Math.trunc(waveformWidth.value * 1.25)
  } else {
    waveformWidth.value = Math.trunc(waveformWidth.value * 0.8)
  }
  nextTick(() => waveform.draw())
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
    document.getElementById(`mark-${offset}`)?.scrollIntoView()
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
  @apply relative overflow-auto;
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
