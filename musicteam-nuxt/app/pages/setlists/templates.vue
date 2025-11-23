<template>
  <div>
    <Head><Title>Set List Templates - MusicTeam</Title></Head>

    <div class="flex flex-row">
      <h1 class="grow">Set List Templates</h1>
      <div>
        <button class="btn-gray" @click="newTemplate">New Template</button>
      </div>
    </div>

    <MtTable
      :columns="templatesColumns"
      :data="templates.data?.templates"
      :row-click="
        (row) => {
          selectedTemplate = row
        }
      "
      :selected="(row) => row.id === selectedTemplate?.id"
    >
      <template #created="{ row }">
        <Created :data="row" />
      </template>
      <template #title="{ row }">
        <MtEditable :model="row" prop="title" @save="saveTemplate(row, 'title')" />
      </template>
      <template #tags="{ row }">
        <MtEditableTags :model="row" @save="saveTemplate(row, 'tags')" />
      </template>
      <template #controls="{ row }">
        <button
          class="hover:text-red-500"
          @click="
            (ev) => {
              deleteTemplate(row)
              ev.stopPropagation()
            }
          "
        >
          <Icon name="ri:delete-bin-6-line" size="20" />
        </button>
      </template>
    </MtTable>

    <SetlistTemplateOrder
      v-if="selectedTemplate"
      :template="selectedTemplate"
      :key="selectedTemplate.id"
    />
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"
import { useToaster } from "@/composables/toast"
import { useSetlistTemplatelistStore } from "@/stores/setlistTemplates"

import type { TableColumn } from "@/types/mt"
import type { SetlistTemplate } from "@/services/api"

const templates = useSetlistTemplatelistStore()
const refreshStore = useSetlistTemplateRefreshStore()

const templatesColumns: TableColumn[] = [
  { name: "created", title: "Created" },
  { name: "title", title: "Title" },
  { name: "tags", title: "Tags" },
  { name: "controls", title: "", cls: "w-24" },
]

const selectedTemplate = ref<SetlistTemplate | null>(null)

async function newTemplate() {
  await useToaster(async () => {
    const resp = await api.setlistTemplates.newSetlistTemplate({
      title: "New Template",
    })
    await api.setlistTemplates.newSetlistTemplatePosition(resp.data.id, {
      index: 1,
      label: "",
      is_music: true,
    })
  })
  await refreshStore.refresh()
}

async function saveTemplate(template: SetlistTemplate, field: keyof SetlistTemplate) {
  await api.setlistTemplates.updateSetlistTemplate(template.id, {
    [field]: template[field],
  })
  await refreshStore.refresh({ templateId: template.id })
}

async function deleteTemplate(template: SetlistTemplate) {
  if (
    !confirm(`Are you sure you want to delete the set list template ${template.title}?`)
  )
    return
  selectedTemplate.value = null
  await api.setlistTemplates.deleteSetlistTemplate(template.id)
  await refreshStore.refresh()
}
</script>
