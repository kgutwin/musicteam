<template>
  <div class="text-slate-400 text-xs text-right pr-8">
    MusicTeam - {{ frontendVersion }}
  </div>
</template>

<script setup lang="ts">
const frontendVersion: string = (window as any).__MUSICTEAM_NUXT_VERSION__
</script>
