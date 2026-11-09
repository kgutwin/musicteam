<template>
  <div v-if="openUpload && canEdit" class="upload-panel">
    <div class="font-bold mr-8">Upload Recording</div>
    <input
      type="file"
      accept="audio/*"
      @change="selectFile"
      :disabled="!!phase"
      data-cy="file"
    />
    <div class="grow relative" :class="{ 'border rounded': !!phase }">
      <div
        v-if="progress"
        :style="`width: ${progress * 100}%`"
        class="h-full bg-blue-500 rounded px-2"
      >
        {{ `${Math.round(progress * 100)}%` }}
      </div>
      <div class="absolute italic top-0 right-4">{{ phase ?? "" }}</div>
    </div>
    <button class="btn-gray" @click="cancel">Cancel</button>
  </div>

  <div>
    <SetlistRecordingEntry
      v-for="recording in recordings?.recordings ?? []"
      :key="recording.id"
      :recording="recording"
    />
    <div v-if="recordings?.recordings?.length === 0" class="div-loading-panel">
      <div class="italic">No recordings uploaded yet</div>
      <div
        v-if="canEdit && !openUpload"
        class="text-base mt-4"
        @click="openUpload = true"
      >
        <button class="btn-gray">Upload a Recording</button>
      </div>
    </div>
    <div v-else-if="recordings?.recordings === undefined" class="div-loading-panel">
      Loading recordings
      <Icon name="svg-spinners:3-dots-fade" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"
import { useSetlistRecordinglistStore, useSetlistRefreshStore } from "@/stores/setlists"
import { audioEncode } from "./ingest"
import { ConversionCanceledError } from "mediabunny"

import type { Conversion } from "mediabunny"

const props = defineProps<{
  setlistId: string
}>()

const openUpload = defineModel<boolean>({ default: false })

const { canEdit } = useRole()

const refreshStore = useSetlistRefreshStore()
const recordings = useSetlistRecordinglistStore().get({
  setlistId: props.setlistId,
}).data

const progress = ref<number>(0)
const phase = ref<string | null>(null)
const conversion = ref<Conversion | null>(null)

async function selectFile(event: any) {
  const file = event.target?.files?.[0] as File | undefined
  if (file) {
    await useToaster(async () => {
      const control = await audioEncode(file, (p, u) => {
        if (u < 0) {
          phase.value = "Uploading..."
        }
        progress.value = p
      })
      conversion.value = control.conversion
      try {
        phase.value = "Converting..."
        await control.conversion.execute()
      } catch (err: any) {
        if (err instanceof ConversionCanceledError) {
          return
        }
        throw err
      }

      const newRecording = {
        ...control.newRecording,
        waveform: JSON.stringify(control.peaks),
      }
      await api.setlists.newSetlistRecording(props.setlistId, newRecording)
      progress.value = 0
      await refreshStore.refresh({ setlistId: props.setlistId })
      phase.value = null
      openUpload.value = false
    })
  }
}

async function cancel() {
  if (conversion.value) {
    await conversion.value.cancel()
  }
  phase.value = null
  progress.value = 0
  openUpload.value = false
}
</script>

<style>
.upload-panel {
  @apply mb-4 p-4 border rounded-lg shadow-lg bg-slate-100;
  @apply flex flex-row gap-2 items-baseline;
}
</style>
