<template>
  <div>
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
          @keyup="(ev) => suggest(ev, index)"
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
        @keydown.enter="(ev) => sepKey(ev)"
        @keydown.space="(ev) => sepKey(ev, allowSpace)"
        @keydown.,="(ev) => sepKey(ev, allowComma)"
        @keydown.delete="delTag"
        @keydown.left="focusLeft"
        @keyup="suggest"
        @blur="addTag"
      >
        {{ disabled ? "&nbsp;" : "" }}
      </div>
    </div>
    <div
      v-if="
        suggestion && getSuggestions && getSuggestions(suggestion.prefix).length > 0
      "
      class="inp-array-suggestion-box"
    >
      <button
        v-for="suggested in getSuggestions(suggestion.prefix)"
        @mousedown="(ev) => ev.preventDefault?.()"
        @click="pickSuggestion(suggested)"
      >
        {{ suggested }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
// vue imports are needed for Cypress component testing
import { nextTick, ref } from "vue"

const props = defineProps<{
  allowSpace?: boolean
  allowComma?: boolean
  disabled?: boolean
  getSuggestions?: (q: string) => string[]
}>()

const tags = defineModel<string[]>({ default: () => [] })

const suggestion = ref<{
  prefix: string
  element: HTMLElement
  index?: number
} | null>(null)

function addTag(ev: Event | HTMLElement, index?: number) {
  if (props.disabled) return
  const target = "target" in ev ? (ev.target as HTMLElement | null) : ev
  if (target && target.textContent.trim()) {
    if (index === undefined) {
      tags.value = [...tags.value, target.textContent.trim()]
    } else {
      tags.value = tags.value.toSpliced(index, 0, target.textContent.trim())
      nextTick(() => {
        const refocus = target.nextElementSibling?.nextElementSibling
        if (refocus) (refocus as HTMLElement).focus()
      })
      if ("preventDefault" in ev) ev.preventDefault()
    }
    target.textContent = ""
    suggestion.value = null
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

function suggest(ev: Event, index?: number) {
  if (props.disabled) return
  const target = ev.target as HTMLElement | null
  if (target && target.textContent.trim().length >= 2) {
    suggestion.value = {
      prefix: target.textContent.trim(),
      element: target,
      index,
    }
  } else {
    suggestion.value = null
  }
}

function pickSuggestion(value: string) {
  if (!suggestion.value) return
  suggestion.value.element.textContent = value
  addTag(suggestion.value.element, suggestion.value.index ?? undefined)
  suggestion.value = null
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

.inp-array-suggestion-box {
  @apply rounded-lg bg-slate-300 px-2 -mt-px mx-2 py-1 shadow-lg;
  @apply flex flex-wrap flex-row gap-2;

  & button {
    @apply block rounded-lg bg-slate-100 px-2 py-px my-1 hover:underline;
  }
}
</style>
