<template>
  <div>
    <UserIcon
      v-for="(n, userId) in posters"
      :user-id="userId"
      class="inline-block -ml-2"
    />
  </div>
</template>

<script setup lang="ts">
import { useCommentlistStore } from "@/stores/comments"

const props = defineProps<{ resourceId: string }>()

const commentStore = useCommentlistStore()

const posters = computed(() =>
  (commentStore.get({ resourceId: props.resourceId }).data?.value?.comments ?? [])
    .map((c) => c.creator_id)
    .reduce((count: Record<string, number>, id) => {
      count[id] = (count[id] ?? 0) + 1
      return count
    }, {}),
)
</script>
