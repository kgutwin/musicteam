<template>
  <div>
    <Head><Title>MusicTeam</Title></Head>
    <h1 class="text-4xl max-sm:text-center">Welcome to MusicTeam!</h1>

    <div class="hero-grid">
      <NuxtLink to="/songs">
        <div>
          <Icon name="solar:music-notes-line-duotone" size="64" />
          <h2>Songs</h2>
          <p>
            Store, share, search, and edit songs. Supports multiple versions and sheets
            per song. Attach media and find similar songs based on lyrics or history.
          </p>
        </div>
      </NuxtLink>

      <NuxtLink to="/setlists">
        <div>
          <Icon name="solar:music-library-line-duotone" size="64" />
          <h2>Set Lists</h2>
          <p>
            Build set lists and assign songs to slots using a friendly candidate-based
            approach. Download auto-assembled PDF & text packets, and upload performance
            recordings.
          </p>
        </div>
      </NuxtLink>

      <NuxtLink to="/history">
        <div>
          <Icon name="solar:graph-new-line-duotone" size="64" />
          <h2>History</h2>
          <p>
            Look at songs rank over time across several metrics. See precise trends in
            song use over multiple years.
          </p>
        </div>
      </NuxtLink>
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
    @apply rounded-3xl shadow-xl bg-sky-100 text-center p-8 h-full;

    & span.iconify {
      @apply mb-4;
    }

    & h2 {
      @apply text-2xl mb-4;
    }
  }
}
</style>
