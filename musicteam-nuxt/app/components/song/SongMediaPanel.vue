<template>
  <div class="text-sm">
    <div
      v-for="entry in media"
      class="pb-2 grid grid-cols-[1em_minmax(150px,1fr)] gap-1 group"
    >
      <div>
        <button v-if="entry.creator_id === authData?.id" class="mt-1">
          <Icon
            name="ri:delete-bin-6-line"
            class="text-gray-500 hover:text-red-500 invisible group-hover:visible"
            @click="deleteMedia(entry.id)"
          />
        </button>
      </div>
      <div class="grow">
        <div
          v-if="entry.url"
          :href="entry.url"
          class="flex flex-row sm:flex-col lg:flex-row"
        >
          <div class="basis-1/2 mr-2">{{ entry.title }}</div>
          <div class="truncate">
            <a :href="entry.url" class="a-hov text-gray-600" target="_blank">
              {{ entry.url }}
            </a>
          </div>
          <Icon
            class="shrink-0 sm:hidden lg:inline"
            name="solar:square-top-down-outline"
          />
        </div>
        <div v-else>
          Under construction...
          <code class="text-xs">
            {{ entry }}
          </code>
          <!-- TODO: API endpoint for fetching media attachment -->
          <!-- TODO: embed if audiovisual, always show download icon -->
        </div>
        <div v-if="(entry.tags?.length ?? 0) > 0">
          <span v-for="tag in entry.tags" :key="tag" class="spn-tag">
            {{ tag }}
          </span>
        </div>
      </div>
    </div>

    <button v-if="canEdit && !adding" class="btn-gray-sm" @click="adding = true">
      Add Media Attachment
    </button>
    <form
      v-else-if="adding"
      @submit.prevent="postMedia"
      class="frm-post grid grid-cols-[3rem_minmax(100px,1fr)] gap-2"
    >
      <div class="col-span-2"><hr class="my-1" /></div>
      <label>Title <span class="spn-req">*</span></label>
      <input v-model="mediaTitle" type="text" class="inp-text" required />

      <div class="col-span-2 w-full flex flex-row gap-2">
        <label class="flex-none block w-12">
          {{ mediaObjectType ? "File" : "URL" }}
        </label>
        <input
          v-if="!mediaObjectType"
          v-model="mediaUrl"
          class="grow inp-text"
          type="url"
          placeholder="https://youtube.com"
          pattern="https://.*"
        />
        <div v-if="!mediaUrl && !mediaObjectType">OR</div>
        <input
          v-if="!mediaUrl"
          ref="input-file"
          class="w-24"
          :class="{ grow: !!mediaObjectType }"
          type="file"
          @change="addFile"
        />
        <button v-if="mediaObjectType" type="button" @click="cancelObject">
          <Icon name="ri:close-large-fill" />
        </button>
      </div>

      <label>Tags</label>
      <MtArrayInput v-model="mediaTags" />

      <div class="col-span-2 flex flex-row gap-2">
        <button class="btn-blue-sm" :disabled="invalid">Add</button>
        <button type="button" class="btn-gray-sm" @click="cancelMedia">Cancel</button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"
import { useSongMedialistStore, useSongMediaRefreshStore } from "@/stores/songs"
import { fileToBase64String } from "@/utils"

import type { ToasterStatus } from "@/types/toast"

const { data: authData } = useAuth()

const props = defineProps<{ songId: string; versionId: string }>()

const { canEdit } = useRole()

const mediaStore = useSongMedialistStore()
const refreshStore = useSongMediaRefreshStore()

const media = computed(
  () =>
    mediaStore.get({ songId: props.songId, versionId: props.versionId }).data?.value
      ?.song_media ?? [],
)

const adding = ref(false)

const mediaTitle = ref<string>()
const mediaUrl = ref<string>()
const mediaTags = ref<string[]>([])

const inputFile = useTemplateRef("input-file")
const mediaObjectId = ref<string>()
const mediaObjectType = ref<string>()
const fileStatus = ref<ToasterStatus>()

function cancelObject() {
  mediaObjectId.value = undefined
  mediaObjectType.value = undefined
  if (inputFile.value) {
    inputFile.value.value = ""
  }
}

async function addFile(event: any) {
  const file = event.target?.files?.[0] as File | undefined
  if (file) {
    mediaUrl.value = undefined
    mediaObjectType.value = file.type
    mediaObjectId.value = await useToaster(
      async () => {
        const encodedFile = await fileToBase64String(file)
        const response = await api.objects.uploadFile(encodedFile, { base64: true })
        return response.data.id
      },
      { errorTitle: "Could not upload file", status: fileStatus },
    )
  }
}

const invalid = useInvalid([mediaTitle], [mediaUrl, mediaTags, mediaObjectId])

function cancelMedia() {
  adding.value = false
  mediaTitle.value = undefined
  mediaUrl.value = undefined
  mediaTags.value = []
  mediaObjectId.value = undefined
  mediaObjectType.value = undefined
  if (inputFile.value) {
    inputFile.value.value = ""
  }
}

async function postMedia() {
  if (invalid.value) return

  await useToaster(async () => {
    await api.songs.newSongMedia(props.songId, props.versionId, {
      title: mediaTitle.value!,
      url: mediaUrl.value,
      object_id: mediaObjectId.value,
      media_type: mediaObjectType.value,
      tags: mediaTags.value,
    })
  })

  cancelMedia()
  await refreshStore.refresh({ songId: props.songId, versionId: props.versionId })
}

async function deleteMedia(mediaId: string) {
  if (!confirm("Are you sure you want to delete this media attachment?")) return

  await useToaster(async () => {
    await api.songs.deleteSongMedia(props.songId, props.versionId, mediaId)
  })
  await refreshStore.refresh({ songId: props.songId, versionId: props.versionId })
}
</script>
