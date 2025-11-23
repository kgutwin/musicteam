<template>
  <div>
    <Head><Title>New Set List - MusicTeam</Title></Head>

    <h1>New Set List</h1>

    <form class="frm-edit">
      <label>
        <span>Leader's Name <span class="spn-req">*</span></span>
        <input v-model="inputLeaderName" class="inp-text" required />
      </label>

      <label>
        <span>Service Date <span class="spn-req">*</span></span>
        <input v-model="inputServiceDate" type="date" class="inp-text" required />
      </label>

      <label>
        <span>Title</span>
        <input v-model="inputTitle" class="inp-text" />
      </label>

      <label>
        <span>Team Participants</span>
        <MtArrayInput v-model="inputParticipants" allow-space />
      </label>

      <label>
        <span>Tags</span>
        <MtArrayInput v-model="inputTags" allow-space />
      </label>
    </form>

    <form class="frm-edit mb-4">
      <div class="flex flex-row mt-2">
        <div class="grow" />
        <div>
          <MtDropdown button-class="btn-gray">
            <template #dropdown-button>Use template...</template>

            <button
              v-for="template in templates.data?.templates ?? []"
              @click="applyTemplate(template.id)"
            >
              {{ template.title }}
            </button>

            <hr />

            <NuxtLink to="/setlists/templates">Edit templates...</NuxtLink>
          </MtDropdown>
        </div>
      </div>

      <MtTable :columns="columns" :data="positions">
        <template #label="{ row }">
          <input v-model="row.label" class="inp-text w-full" required />
        </template>
        <template #presenter="{ row }">
          <input v-model="row.presenter" class="inp-text w-full" />
        </template>
        <template #is-music="{ row }">
          <input type="checkbox" v-model="row.is_music" tabindex="0" />
        </template>
        <template #controls="{ row, index }">
          <div class="flex flex-row mt-1 gap-2">
            <button
              type="button"
              tabindex="0"
              @click="
                positions.splice(index + 1, 0, {
                  id: randomId(),
                  index: index + 1,
                  is_music: true,
                })
              "
            >
              <Icon name="ri:add-large-line" size="20" />
            </button>
            <button type="button" @click="positions.splice(index, 1)">
              <Icon name="ri:delete-bin-6-line" size="20" />
            </button>
          </div>
        </template>
      </MtTable>
    </form>

    <div class="flex flex-row gap-2">
      <button class="btn-gray" @click="save" :disabled="invalid || saving">
        Save
        <Icon v-if="saving" name="svg-spinners:270-ring-with-bg" class="ml-4" />
      </button>
      <button class="btn-gray" @click="cancel">Cancel</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { NewSetlistPosition } from "@/services/api"
import type { TableColumn } from "@/types/mt"

import { api } from "@/services"
import { nextSunday, randomId } from "@/utils"
import { useSetlistRefreshStore } from "@/stores/setlists"
import { useSetlistTemplatelistStore } from "@/stores/setlistTemplates"
import { useSetlistTemplatePositionlistStore } from "@/stores/setlistTemplates"

const { data: authData } = useAuth()

const setlistRefresh = useSetlistRefreshStore()
const templates = useSetlistTemplatelistStore()
const templatePositionStore = useSetlistTemplatePositionlistStore()

const inputLeaderName = ref<string | undefined>(authData.value?.name)
const inputServiceDate = ref<string>(nextSunday())
const inputTitle = ref<string>()
const inputParticipants = ref<string[]>([])
const inputTags = ref<string[]>([])

type PendingPosition = Partial<NewSetlistPosition> & { id: string }

const positions = ref<PendingPosition[]>([{ id: randomId(), index: 1, is_music: true }])
const columns: TableColumn[] = [
  { name: "presenter", title: "Presenter" },
  { name: "label", title: "Label", required: true },
  { name: "is-music", title: "Needs Music?" },
  { name: "controls", title: "" },
]

watch(
  positions,
  (newV) => {
    if (newV.length === 0) {
      positions.value = [{ id: randomId(), index: 1, is_music: true }]
    }
  },
  { deep: true },
)

async function applyTemplate(templateId: string) {
  const tpl = await templatePositionStore.get({ templateId }).get()
  positions.value = tpl.positions.map(({ id, index, is_music, label, presenter }) => ({
    id,
    index,
    is_music,
    label,
    presenter,
  }))
}

const invalid = useInvalid([inputLeaderName, inputServiceDate, positions])

const saving = ref(false)

async function save() {
  saving.value = true

  const leaderName = inputLeaderName.value
  const serviceDate = inputServiceDate.value
  const title = inputTitle.value
  const participants = inputParticipants.value
  const tags = inputTags.value

  if (!leaderName) return

  const setlistResponse = await api.setlists.newSetlist({
    leader_name: leaderName,
    service_date: serviceDate,
    title,
    participants,
    tags,
  })

  const setlistId = setlistResponse.data.id

  let index = 1
  const promises = []
  for (const position of positions.value as NewSetlistPosition[]) {
    position.index = index
    promises.push(api.setlists.newSetlistPosition(setlistId, position))
    index += 1
  }
  await Promise.all(promises)

  await setlistRefresh.refresh()

  saving.value = false

  await navigateTo({ path: `/setlists/${setlistId}` })
}

async function cancel() {
  await navigateTo({ path: "/setlists" })
}
</script>
