<template>
  <div class="p-8 text-xl bg-blue-200 flex flex-row gap-4">
    <div><NuxtLink to="/">MusicTeam</NuxtLink></div>
    <div class="grow"><NuxtLink to="/songs">Songs</NuxtLink></div>
    <div>
      <button v-if="status === 'authenticated'" @click="signOut({ callbackUrl: '/' })">
        Logout
      </button>
      <NuxtLink v-else to="/login">Sign In</NuxtLink>
    </div>
    <div v-if="authData?.picture">
      <img :src="authData.picture" class="h-12 w-12 rounded-full" />
    </div>
  </div>
</template>

<script setup lang="ts">
const { status, signOut, data: authData } = useAuth()
</script>
