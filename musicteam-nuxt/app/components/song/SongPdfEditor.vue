<template>
  <pdfjs-viewer-element
    ref="viewer"
    class="h-screen"
    :src="`/api/songs/${songId}/versions/${versionId}/sheets/${sheetId}/doc`"
    viewer-path="/pdfjs-5"
  ></pdfjs-viewer-element>
</template>

<script setup lang="ts">
import "pdfjs-viewer-element"

defineProps<{
  songId: string
  versionId: string
  sheetId: string
}>()

const emit = defineEmits<{ hasSave: [() => Promise<Blob>] }>()

const viewer = useTemplateRef("viewer")

onMounted(async () => {
  if (!viewer.value) return

  const viewerApp = await viewer.value.initialize()

  viewerApp.eventBus.on("pagesloaded", () => {
    emit(
      "hasSave",
      async () =>
        new Blob([await viewerApp.pdfDocument.saveDocument()], {
          type: "application/pdf",
        }),
    )
  })
})
</script>
