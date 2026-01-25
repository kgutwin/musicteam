<template>
  <svg
    width="120"
    height="32"
    version="1.1"
    xmlns="http://www.w3.org/2000/svg"
    class="rounded shadow-inner"
  >
    <rect :x="lastYearStart" y="0" width="60" height="32" class="fill-slate-100" />

    <rect
      v-for="bar in bars"
      :x="bar.x"
      :y="32 - bar.h"
      width="4"
      :height="bar.h"
      class="fill-blue-500"
    />
  </svg>
</template>

<script setup lang="ts">
import type { SparkLineHistoryPoint } from "@/services/api"

const props = defineProps<{
  data: SparkLineHistoryPoint[] | undefined
}>()

const today = new Date()
const thisMonth = today.getFullYear() * 12 + today.getMonth() + 1

function dateToXpos(date: string) {
  // months are 5 px wide (4 px bar, 1 px gap)
  const [year, month, day] = date.split("-").map((v) => parseInt(v))
  if (!year || !month) return -1
  let months = thisMonth - (year * 12 + month)
  return 120 - (months + 1) * 5
}

const lastYearStart = dateToXpos(`${today.getFullYear() - 1}-01-01`)

const barHeight = [0, 12, 18, 25, 32]

const bars = computed(() => {
  if (!props.data) return []
  return props.data.map((pt) => ({
    x: dateToXpos(pt.mo_yr),
    h: pt.count > 4 ? 32 : (barHeight[pt.count] ?? 0),
  }))
})
</script>
