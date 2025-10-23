<template>
  <table class="mt-table">
    <thead>
      <tr>
        <th v-for="column in columns" :key="column.name" :class="column.cls">
          {{ column.title }}
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(row, index) in data" :key="index">
        <td v-for="column in columns" :key="column.name" :class="column.cls">
          <slot :name="column.name" :row="row" :index="index" />
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts" generic="T">
import type { TableColumn } from "@/types/mt"

defineProps<{
  columns: TableColumn[]
  data: T[]
}>()
</script>

<style>
.mt-table {
  @apply border m-4 w-full shadow-lg;

  & tbody {
    @apply divide-y border border-gray-300;

    & tr td {
      @apply p-2;
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
