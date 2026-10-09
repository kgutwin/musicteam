<template>
  <button title="Copy to Clipboard" @click="copyToClipboard" @mouseout="copied = false">
    <slot v-if="copied" name="copied">
      <Icon name="solar:clipboard-check-linear" class="text-green-700" />
    </slot>
    <slot v-else>
      <Icon :name="iconName ?? 'solar:clipboard-text-linear'" />
    </slot>
  </button>
</template>

<script setup lang="ts">
const props = defineProps<{
  content: string | (() => string | undefined) | (() => Promise<string | undefined>)
  contentType?: string
  iconName?: string
}>()

const copied = ref(false)

async function copyToClipboard() {
  const content: string | undefined =
    typeof props.content === "string" ? props.content : await props.content()

  if (content !== undefined) {
    copied.value = true
    if (props.contentType) {
      const clipboardItem = new ClipboardItem({ [props.contentType]: content })
      await navigator.clipboard.write([clipboardItem])
    } else {
      await navigator.clipboard.writeText(content)
    }
  }
}
</script>
