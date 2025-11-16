<template>
  <div class="inp-text inp-array">
    <!-- <div class="min-w-px"></div> -->
    <div
      v-for="(tag, index) in tags"
      class="inp-array-el group"
      :disabled="disabled"
      contenteditable="false"
      tabindex="0"
      @keydown.delete="
        () => {
          tags = tags.toSpliced(index, 1)
        }
      "
    >
      {{ tag }}
      <div
        v-if="!disabled"
        class="remove hidden group-hover:inline cursor-pointer"
        @click="
          () => {
            tags = tags.toSpliced(index, 1)
          }
        "
      >
        X
      </div>
    </div>
    <div
      ref="newTagRef"
      class="inp-array-newtag"
      :contenteditable="disabled ? 'false' : 'plaintext-only'"
      @keydown.enter="addTag"
      @keydown.space="
        (ev) => {
          if (!allowSpace) {
            addTag()
            ev.preventDefault()
          }
        }
      "
      @keydown.,="
        (ev) => {
          if (!allowComma) {
            addTag()
            ev.preventDefault()
          }
        }
      "
      @keydown.delete="
        (ev) => {
          if (!newTagRef?.textContent) {
            tags.pop()
            ev.preventDefault()
          }
        }
      "
      @blur="addTag"
    >
      {{ disabled ? "&nbsp;" : "" }}
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  allowSpace?: boolean
  allowComma?: boolean
  disabled?: boolean
}>()

const tags = defineModel<string[]>({ default: [] })

const newTagRef = useTemplateRef("newTagRef")

function addTag() {
  if (newTagRef.value && newTagRef.value.textContent.trim()) {
    tags.value = [...tags.value, newTagRef.value.textContent.trim()]
    newTagRef.value.textContent = ""
  }
}
</script>

<style>
.inp-array {
  @apply flex flex-wrap flex-row bg-white gap-2;
}
.inp-array:has(.inp-array-newtag:focus) {
  @apply ring-blue-400 ring;
}
.inp-array-el {
  @apply inline-block relative rounded-full bg-purple-200 pl-4 pr-6;
}
.inp-array-el[disabled="true"] {
  @apply bg-gray-200;
}
.inp-array-el > .remove {
  @apply absolute top-1 right-2 text-white text-xs;
}
.inp-array-newtag {
  @apply grow min-w-px; /* focus:border-transparent focus:ring-0; */
}
.inp-array-newtag:focus {
  outline: 0;
}
</style>
