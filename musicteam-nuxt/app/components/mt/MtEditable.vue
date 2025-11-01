<template>
  <div class="inline-block group/edit">
    <template v-if="!editing">
      <MtText is="span" :text="model?.[prop]" loading="w-48" />
      <button
        v-if="model"
        class="invisible group-hover/edit:visible text-base ml-2"
        @click="editing = true"
      >
        <Icon name="solar:pen-linear" />
      </button>
    </template>
    <template v-else>
      <input
        class="inp-text"
        :type="type"
        v-model="editableValue"
        @keydown.enter="save"
      />
      <button type="button" class="ml-2" @click="save">
        <Icon name="ri:check-line" />
      </button>
      <button type="button" @click="editing = false">
        <Icon name="ri:close-line" />
      </button>
    </template>
  </div>
</template>

<script setup lang="ts" generic="T, K extends keyof T">
// import { tryUpdateModel } from "@/services"

const props = defineProps<{
  is?: string
  model?: T & Partial<Record<K, string | null>>
  prop: K
  type?: "text" | "date"
}>()

const emit = defineEmits<{ save: [newV: any] }>()

const editing = ref(false)
const editableValue = ref<any>()
watch(editing, (newV, oldV) => {
  if (newV && !oldV && props.model) {
    editableValue.value = props.model[props.prop]
  }
})

async function save() {
  if (!props.model) return

  // patch model first
  props.model[props.prop] = editableValue.value

  // await tryUpdateModel(props.model, props.prop)

  emit("save", editableValue.value)

  editing.value = false
}
</script>
