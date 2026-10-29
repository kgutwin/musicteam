<template>
  <div v-if="canEdit" class="mb-4">
    <button v-if="!adding" class="btn-gray" @click="adding = true">
      Upload Recording
    </button>
    <div v-else class="upload-panel">
      <div class="font-bold mr-8">Upload Recording</div>
      <input type="file" accept="audio/*" @change="selectFile" />
      <div class="grow" :class="{ 'border rounded': !!progress }">
        <div
          v-if="progress"
          :style="`width: ${progress * 100}%`"
          class="h-full bg-blue-500 rounded px-2"
        >
          {{ `${Math.round(progress * 100)}%` }}
        </div>
      </div>
      <button class="btn-gray" @click="cancel">Cancel</button>
    </div>
  </div>

  <div>
    <SetlistRecordingEntry
      v-for="recording in recordings?.recordings ?? []"
      :key="recording.id"
      :recording="recording"
    />
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"
import { useSetlistRecordinglistStore, useSetlistRefreshStore } from "@/stores/setlists"
import { audioEncode } from "./ingest"
import { ConversionCanceledError } from "mediabunny"

import type { Conversion } from "mediabunny"

const props = defineProps<{ setlistId: string }>()

const { canEdit } = useRole()

const refreshStore = useSetlistRefreshStore()
const recordings = useSetlistRecordinglistStore().get({
  setlistId: props.setlistId,
}).data

const adding = ref(false)
const progress = ref<number>()
const conversion = ref<Conversion | null>(null)

async function selectFile(event: any) {
  const file = event.target?.files?.[0] as File | undefined
  if (file) {
    await useToaster(async () => {
      const control = await audioEncode(file, (p) => {
        progress.value = p
      })
      conversion.value = control.conversion
      try {
        await control.conversion.execute()
      } catch (err: any) {
        if (err instanceof ConversionCanceledError) {
          return
        }
        throw err
      }

      await api.setlists.newSetlistRecording(props.setlistId, control.newRecording)
      await refreshStore.refresh({ setlistId: props.setlistId })
      adding.value = false
    })
  }
}

async function cancel() {
  if (conversion.value) {
    await conversion.value.cancel()
  }
  adding.value = false
}
</script>

<style>
.upload-panel {
  @apply p-4 border rounded shadow-lg bg-slate-100 flex flex-row gap-2 items-baseline;
}
</style>
