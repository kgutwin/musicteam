<template>
  <form class="frm-edit relative">
    <button class="absolute right-3 top-3" type="button" @click="emit('remove')">
      <Icon name="ri:delete-bin-6-line" />
    </button>

    <label>
      <span>Music Sheet Type <span class="spn-req">*</span></span>
      <MtSelectOther
        v-model="inputSheetType"
        :options="['Chord', 'Lead', 'Vocal', 'Hymn']"
      />
    </label>

    <label>
      <span>Musical Key <span class="spn-req">*</span></span>
      <input v-model="inputKey" class="inp-text" required placeholder="C" />
    </label>

    <label>
      <span>Music Sheet Tags</span>
      <MtArrayInput v-model="inputSheetTags" allow-space />
    </label>

    <label v-if="!useTextEditor">
      <span>Select File</span>
      <div class="flex flex-row gap-2 items-baseline">
        <input
          type="file"
          accept="text/plain, application/pdf, application/vnd.recordare.musicxml+xml"
          @change="addFile"
        />
        <Icon
          v-if="fileStatus === 'pending'"
          name="svg-spinners:270-ring-with-bg"
          size="24"
        />
        <Icon
          v-if="inputObjectId"
          name="ri:file-check-line"
          size="24"
          class="text-green-500"
        />
	<span class="mr-4">or</span>
	<button type="button" class="btn-gray" @click="useTextEditor = true">
	  Use Text Editor
	</button>
      </div>
    </label>

    <label v-else>
      <span>Text Sheet Contents</span>
      <div class="flex flex-row gap-4 items-start">
        <SongTextEditor :short="true" class="grow" @has-save="(save) => (saveTextFile = save)" />
	<div class="flex flex-col gap-4">
	  <button type="button" class="btn-blue" @click="addFile()">
	    Save Sheet
            <Icon
              v-if="inputObjectId"
              name="ri:file-check-line"
              class="ml-2 text-green-600"
            />
	  </button>
  	  <button type="button" class="btn-gray" @click="useTextEditor = false">
 	    Upload File
	  </button>
	</div>
      </div>
    </label>

    <label>
      <span>Does music sheet already include verse order?</span>
      <select v-model="inputAutoVerseOrder" class="sel-dropdown">
        <option value="true">Sheet does not have verse order</option>
        <option value="false">Sheet already has verse order</option>
      </select>
    </label>
  </form>
</template>

<script setup lang="ts">
import { api } from "@/services"
import { fileToBase64String } from "@/utils"

import type { NewSongSheet } from "@/services/api"
import type { ToasterStatus } from "@/types/toast"

const sheet = defineModel<Partial<NewSongSheet>>()

const emit = defineEmits<{ remove: [] }>()

const inputSheetType = ref<string>()
const inputKey = ref<string>()
const inputObjectId = ref<string>()
const inputObjectType = ref<string>()
const inputAutoVerseOrder = ref<string>("true")
const inputSheetTags = ref<string[]>([])

const useTextEditor = ref(false)
const saveTextFile = ref<() => Promise<Blob>>()
const fileStatus = ref<ToasterStatus>()

async function addFile(event?: any) {
  const file = useTextEditor.value && saveTextFile.value
    ? await saveTextFile.value()
    : event?.target?.files?.[0] as File | undefined

  if (file) {
    inputObjectType.value = file.type
    inputObjectId.value = await useToaster(
      async () => {
        const encodedFile = await fileToBase64String(file)
        const response = await api.objects.uploadFile(encodedFile, { base64: true })
        return response.data.id
      },
      { errorTitle: "Could not upload file", status: fileStatus },
    )
  }
}

watchEffect(() => {
  sheet.value = {
    type: inputSheetType.value,
    key: inputKey.value,
    object_id: inputObjectId.value,
    object_type: inputObjectType.value,
    auto_verse_order: inputAutoVerseOrder.value === "true",
    tags: inputSheetTags.value,
  }
})
</script>
