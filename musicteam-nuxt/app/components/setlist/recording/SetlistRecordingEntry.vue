<template>
  <div class="my-8">
    <div class="flex flex-row gap-2 items-baseline mb-2">
      <div>Uploaded: {{ recording.created_on }}</div>
      <button class="btn-gray" @click="deleteEntry">Delete</button>
      <button class="btn-gray" @click="download">Download</button>
      <button class="btn-gray" @click="load">Load</button>
    </div>
    <audio :src="url" controls class="w-full" />
    <div class="recording-scroller">
      <canvas ref="canvas" class="recording-waveform" width="1470" height="150" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"
import { useSetlistRefreshStore } from "@/stores/setlists"
import mime from "mime-types"
import { WaveformViewer } from "./waveform"

import type { SetlistRecording } from "@/services/api"

const props = defineProps<{ recording: SetlistRecording }>()

const refreshStore = useSetlistRefreshStore()

const url = computed(
  () =>
    `/api/setlists/${props.recording.setlist_id}/recordings/${props.recording.id}/audio`,
)

const canvas = useTemplateRef("canvas")
const waveform = new WaveformViewer(url.value)
watchEffect(() => {
  if (canvas.value) {
    waveform.setCanvas(canvas.value)
  }
})

async function deleteEntry() {
  await api.setlists.deleteSetlistRecording(
    props.recording.setlist_id,
    props.recording.id,
  )
  await refreshStore.refresh({ setlistId: props.recording.setlist_id })
}

async function download() {
  let ext = mime.extension(props.recording.audio_object_type)

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

async function load() {
  await waveform.load()
  waveform.draw()
}
</script>

<style>
.recording-scroller {
  @apply overflow-auto;
}
.recording-waveform {
  @apply mt-1 block border rounded; /* scale-x-150 origin-left; */
  image-rendering: pixelated;
}
</style>
