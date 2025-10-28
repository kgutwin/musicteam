<template>
  <div>
    <h1 class="text-4xl">Welcome to MusicTeam!</h1>

    <div class="hero-grid">
      <div>
        <Icon name="solar:music-notes-line-duotone" size="64" />
        <h2>Songs</h2>
        <p>
          Store, share, search, and edit songs. Supports multiple versions and sheets
          per song.
        </p>
      </div>
      <div>
        <Icon name="solar:music-library-line-duotone" size="64" />
        <h2>Set Lists</h2>
        <p>
          Build set lists from templates, and assign songs to slots using a friendly
          candidate-based approach. Download auto-assembled PDF & text packets to
          distribute to the team.
        </p>
      </div>
      <div>
        <Icon name="solar:graph-new-line-duotone" size="64" />
        <h2>History</h2>
        <p>Track usage of songs over time.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ auth: false })
</script>

<style>
.hero-grid {
  @apply mt-8 grid grid-cols-1 lg:grid-cols-3 gap-12;

  & div {
    @apply rounded-3xl shadow-xl bg-sky-100 text-center p-8;

    & span.iconify {
      @apply mb-4;
    }

    & h2 {
      @apply text-2xl mb-4;
    }
  }
}
</style>
