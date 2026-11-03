<template>
  <button @click="model = !model">
    <Icon :name="iconName" />
  </button>
</template>

<script setup lang="ts">
import { useCommentlistStore } from "@/stores/comments"

const props = defineProps<{ resourceId: string }>()
const model = defineModel<boolean>()

const commentStore = useCommentlistStore()

const iconName = computed(() => {
  const hasComments =
    (commentStore.get({ resourceId: props.resourceId }).data.value?.comments ?? [])
      .length > 0
  switch (`${hasComments} ${model.value}`) {
    case "false false":
      return "solar:chat-round-linear"
    case "false true":
      return "solar:chat-round-bold"
    case "true false":
      return "solar:chat-round-like-line-duotone"
    case "true true":
      return "solar:chat-round-like-bold-duotone"
  }
  return "solar:chat-dots-linear"
})
</script>
