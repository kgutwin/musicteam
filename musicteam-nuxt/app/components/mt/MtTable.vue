<template>
  <table class="mt-table">
    <thead>
      <tr>
        <th v-for="column in columns" :key="column.name" :class="column.cls">
          {{ column.title }}
          <span v-if="column.required" class="spn-req">*</span>
        </th>
      </tr>
    </thead>
    <draggable
      v-if="data"
      v-model="draggableData"
      tag="tbody"
      handle=".drag-handle"
      @end="(ev) => $emit('dragEnd', ev)"
    >
      <tr
        v-for="(row, index) in data"
        :key="row.id"
        :clickable="!!rowClick"
        :selected="selected?.(row) ?? false"
        @click="
          () => {
            if (rowClick) {
              rowClick(row)
            }
          }
        "
      >
        <td v-for="column in columns" :key="column.name" :class="column.cls">
          <slot :name="column.name" :row="row" :index="index" />
        </td>
      </tr>
    </draggable>
    <tbody v-else>
      <tr>
        <td :colspan="columns.length">
          <div class="w-full text-center italic p-2">
            Loading
            <Icon name="svg-spinners:3-dots-fade" class="ml-4" />
          </div>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts" generic="T extends { id: string }">
import { VueDraggableNext as draggable, type SortableEvent } from "vue-draggable-next"

import type { TableColumn } from "@/types/mt"

const props = defineProps<{
  columns: TableColumn[]
  data?: T[]
  rowClick?: (row: T) => any
  selected?: (row: T) => boolean
}>()

defineEmits<{ dragEnd: [SortableEvent] }>()

const draggableData = computed({
  get() {
    return props.data
  },
  set(newV) {},
})
</script>

<style>
.mt-table {
  @apply border my-4 w-full shadow-lg;

  & tbody {
    @apply divide-y border border-gray-300;

    & tr {
      @apply bg-gray-50;
      & td {
        @apply p-2;
      }
    }
    & tr[clickable="true"] {
      @apply hover:bg-gray-100;
    }
    & tr[selected="true"] {
      @apply bg-blue-100;
    }
    & tr[clickable="true"][selected="true"] {
      @apply hover:bg-blue-100;
    }
  }

  & thead {
    @apply bg-slate-200 text-left;

    & tr th {
      @apply p-2;
    }
  }
}
</style>
