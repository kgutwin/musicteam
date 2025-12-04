<template>
  <div class="text-sm">
    <div
      v-for="comment in comments"
      class="pb-2 mb-2 border-b border-black flex flex-row gap-2 group"
    >
      <div class="flex flex-col gap-1">
        <UserIcon :user-id="comment.creator_id" />
        <button
          v-if="comment.creator_id === authData?.id"
          @click="deleteComment(comment.id)"
        >
          <Icon
            name="ri:delete-bin-6-line"
            class="text-gray-500 hover:text-red-500 invisible group-hover:visible"
          />
        </button>
      </div>
      <div class="grow">
        <div class="flex flex-row">
          <div class="grow italic">
            {{ userStore.get({ userId: comment.creator_id }).data?.value?.name }}
          </div>
          <div>{{ localdate(comment.created_on) }}</div>
        </div>
        <div class="whitespace-pre-line">{{ comment.comment }}</div>
      </div>
    </div>
    <button v-if="!adding" class="btn-gray-sm" @click="adding = true">
      Add Comment
    </button>
    <form v-else @submit.prevent="postComment">
      <textarea v-model="commentText" class="text-sm w-full p-1" />
      <button class="btn-blue-sm">Post</button>
      <button type="button" class="btn-gray-sm" @click="cancelPost">Cancel</button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"
import { useCommentlistStore, useCommentRefreshStore } from "@/stores/comments"
import { useUserStore } from "@/stores/users"
import { localdate } from "@/utils"

const { data: authData } = useAuth()

const props = defineProps<{ resourceId: string }>()

const userStore = useUserStore()
const commentStore = useCommentlistStore()
const refreshStore = useCommentRefreshStore()

const comments = computed(
  () => commentStore.get({ resourceId: props.resourceId }).data?.value?.comments ?? [],
)

const adding = ref(false)
const commentText = ref("")

async function postComment() {
  await useToaster(async () => {
    await api.comments.newComment(props.resourceId, { comment: commentText.value })
  })
  adding.value = false
  commentText.value = ""
  await refreshStore.refresh({ resourceId: props.resourceId })
}

function cancelPost() {
  adding.value = false
  commentText.value = ""
}

async function deleteComment(commentId: string) {
  if (!confirm("Are you sure you want to delete this comment?")) return

  await useToaster(async () => {
    await api.comments.deleteComment(props.resourceId, commentId)
  })
  await refreshStore.refresh({ resourceId: props.resourceId })
}
</script>
