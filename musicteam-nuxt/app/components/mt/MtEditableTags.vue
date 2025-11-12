<template>
  <MtEditable :model="model" prop="tags" @save="$emit('save')">
    <div class="flex flex-row flex-wrap">
      <span v-if="(model?.tags ?? []).length === 0" class="italic text-gray-400">
        No tags
      </span>
      <span v-for="tag in model?.tags ?? []" :key="tag" class="spn-tag">
        {{ tag }}
      </span>
    </div>

    <template #input="{ modelValue, updateModelValue }">
      <MtArrayInput
        class="min-w-24"
        :modelValue="modelValue"
        @update:modelValue="updateModelValue"
        allow-space
      />
    </template>
  </MtEditable>
</template>

<script setup lang="ts">
defineProps<{ model?: { tags?: string[] } }>()
defineEmits<{ save: [] }>()
</script>
