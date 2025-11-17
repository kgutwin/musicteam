<template>
  <div class="inp-text inp-array">
    <template v-for="(tag, index) in tags">
      <div
        class="inp-array-inserttag"
        :contenteditable="disabled ? 'false' : 'plaintext-only'"
        @keydown.enter="(ev) => addTag(ev, index)"
        @keydown.space="(ev) => sepKey(ev, allowSpace, index)"
        @keydown.,="(ev) => sepKey(ev, allowComma, index)"
        @keydown.left="focusLeft"
        @keydown.right="focusRight"
        @keydown.delete="(ev) => delTag(ev, index - 1)"
        @blur="(ev) => addTag(ev, index)"
      ></div>
      <div
        class="inp-array-el group"
        :disabled="disabled"
        contenteditable="false"
        tabindex="0"
        @keydown.left="focusLeft"
        @keydown.right="focusRight"
        @keydown.delete="(ev) => delTag(ev, index)"
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
    </template>
    <div
      class="inp-array-newtag"
      :contenteditable="disabled ? 'false' : 'plaintext-only'"
      @keydown.enter="addTag"
      @keydown.space="(ev) => sepKey(ev, allowSpace)"
      @keydown.,="(ev) => sepKey(ev, allowComma)"
      @keydown.delete="delTag"
      @keydown.left="focusLeft"
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

function addTag(ev: Event, index?: number) {
  if (props.disabled) return
  const target = ev.target as HTMLElement | null
  if (target && target.textContent.trim()) {
    if (index === undefined) {
      tags.value = [...tags.value, target.textContent.trim()]
    } else {
      tags.value = tags.value.toSpliced(index, 0, target.textContent.trim())
      nextTick(() => {
        const refocus = target.nextElementSibling?.nextElementSibling
        if (refocus) (refocus as HTMLElement).focus()
      })
      ev.preventDefault()
    }
    target.textContent = ""
  }
}

function sepKey(ev: Event, check?: boolean, index?: number) {
  if (props.disabled) return
  if (!check) {
    addTag(ev, index)
    ev.preventDefault()
  }
}

function delTag(ev: Event, index?: number) {
  if (props.disabled) return
  const target = ev.target as HTMLElement | null
  if (!target) return
  if (!target.textContent || target.classList.contains("inp-array-el")) {
    if (index === undefined) {
      tags.value = tags.value.toSpliced(-1, 1)
    } else if (index >= 0) {
      tags.value = tags.value.toSpliced(index, 1)
      nextTick(() => {
        // FIXME: something is weird with how this works when using the delete key
        // on a focused tag element. Also inconsistent between Safari and Chrome.
        // Interestingly, it works fine on Firefox.
        const refocus = target.previousElementSibling?.previousElementSibling
        if (refocus) (refocus as HTMLElement).focus()
      })
    }
    ev.preventDefault()
  }
}

function focusLeft(ev: Event) {
  const sel = window.getSelection()
  if (sel?.anchorOffset === 0) {
    const target = ev.target as HTMLElement | null
    if (target?.previousElementSibling)
      (target.previousElementSibling as HTMLElement).focus()
  }
}

function focusRight(ev: Event) {
  const sel = window.getSelection()
  if (!sel) return
  const atRight = sel.focusNode
    ? sel.focusOffset === ((sel.focusNode as Text).data?.length ?? 0)
    : true
  if (atRight) {
    const target = ev.target as HTMLElement | null
    if (target?.nextElementSibling) (target.nextElementSibling as HTMLElement).focus()
  }
}
</script>

<style>
.inp-array {
  @apply flex flex-wrap flex-row bg-white gap-1;
}
.inp-array:has(.inp-array-newtag:focus, .inp-array-inserttag:focus) {
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
  @apply grow min-w-px;
}

.inp-array-newtag:focus,
.inp-array-inserttag:focus {
  outline: 0;
}
.inp-array-inserttag {
  @apply focus:min-w-px;
}
</style>
