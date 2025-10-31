<template>
  <div
    class="px-8 py-4 text-xl bg-gradient-to-tr from-blue-300 to-sky-200 flex flex-row gap-4 items-baseline"
  >
    <div
      class="text-3xl italic font-extrabold tracking-tight text-sky-700 bg-sky-100 rounded-lg shadow-lg px-4 py-1 mr-12"
    >
      <NuxtLink to="/">MusicTeam</NuxtLink>
    </div>
    <div class="grow flex flex-row gap-8 font-semibold tracking-wide">
      <NuxtLink to="/songs">Songs</NuxtLink>
      <NuxtLink to="/setlists">Set Lists</NuxtLink>
      <NuxtLink to="/team">Team</NuxtLink>
    </div>
    <div v-if="status === 'authenticated'" class="self-start">
      <NuxtLink v-if="authData" to="/my/profile">
        <img
          v-if="authData?.picture"
          :src="authData.picture"
          :alt="authData.name"
          class="h-12 w-12 rounded-full"
          referrerpolicy="no-referrer"
        />
        <span v-else>{{ authData.name.split(/\s+/)[0] }}</span>
      </NuxtLink>
    </div>
    <div v-else>
      <NuxtLink to="/login">Sign In</NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
const { status, signOut, data: authData } = useAuth()
</script>
