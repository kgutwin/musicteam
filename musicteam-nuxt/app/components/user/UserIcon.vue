<template>
  <div>
    <img
      v-if="user?.picture && showPicture"
      :src="user.picture"
      :alt="user?.name"
      class="user-icon"
      :class="{ large }"
      referrerpolicy="no-referrer"
      @error="showPicture = false"
    />
    <div
      v-else
      class="user-icon as-text"
      :class="{ large }"
      :style="{ 'background-color': color }"
    >
      {{ large ? user?.name : user?.name?.substring(0, 1) }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from "@/stores/users"
import randomColor from "randomcolor"

const props = defineProps<{
  userId: string
  large?: boolean
}>()

const userStore = useUserStore()

const showPicture = ref(true)

const user = computed(() => userStore.get({ userId: props.userId }).data?.value)
const color = computed(() => randomColor({ seed: props.userId, luminosity: "light" }))
</script>

<style>
.user-icon {
  @apply h-6 w-6 rounded-full;
}
.user-icon.large {
  @apply h-12 w-12;
}
.user-icon.as-text {
  @apply flex items-center text-xs justify-center text-center font-bold;
}
</style>
