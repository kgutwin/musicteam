<template>
  <div class="inline-block group/edit">
    <div class="flex flex-row items-baseline">
      <template v-if="!editing">
        <slot>
          <MtText is="span" :text="getText()" :loading="wide ? 'w-72' : 'w-48'" />
        </slot>
        <button
          v-if="model"
          class="invisible group-hover/edit:visible text-base ml-2"
          @click="editing = true"
        >
          <Icon name="solar:pen-linear" />
        </button>
      </template>
      <template v-else>
        <slot
          name="input"
          :modelValue="editableValue"
          :update-model-value="(newV: T[K]) => (editableValue = newV)"
          :save="save"
        >
          <input
            class="inp-text"
            :type="type"
            v-model="editableValue"
            @keydown.enter="save"
          />
        </slot>
        <button type="button" class="ml-2" @click="save">
          <Icon name="ri:check-line" />
        </button>
        <button type="button" @click="editing = false">
          <Icon name="ri:close-line" />
        </button>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts" generic="T, K extends keyof T">
// import { tryUpdateModel } from "@/services"

const props = defineProps<{
  is?: string
  model?: T & Partial<Record<K, string | string[] | number | null>>
  prop: K
  type?: "text" | "date"
  wide?: boolean
}>()

const emit = defineEmits<{ save: [newV: T[K]] }>()

const editing = ref(false)
const editableValue = ref<T[K]>()
watch(editing, (newV, oldV) => {
  if (newV && !oldV && props.model) {
    editableValue.value = props.model[props.prop]
  }
})

function getText(): string | null | undefined {
  const propv = props.model?.[props.prop]
  if (propv === null || propv === undefined) return propv

  if (props.type === "date" && typeof propv === "string") {
    return localdate(propv)
  } else if (Array.isArray(propv)) {
    return propv.join(", ")
  }
  return propv.toString()
}

async function save() {
  if (!props.model) return
  if (!editableValue.value) return

  // patch model first
  props.model[props.prop] = editableValue.value as any

  // await tryUpdateModel(props.model, props.prop)

  emit("save", editableValue.value)

  editing.value = false
}
</script>
