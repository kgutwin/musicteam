<template>
  <div
    class="px-4 sm:px-8 py-4 text-xl bg-gradient-to-tr from-blue-300 to-sky-200 flex flex-row gap-4 items-baseline"
  >
    <div
      class="text-3xl italic font-extrabold tracking-tight text-sky-700 bg-sky-100 rounded-lg shadow-lg px-4 py-1 mr-4 md:mr-12"
    >
      <NuxtLink to="/">
        M<span class="hide-sm">usic</span>T<span class="hide-sm">eam</span>
      </NuxtLink>
    </div>
    <div class="grow flex flex-row gap-4 md:gap-8 font-semibold tracking-wide">
      <NuxtLink to="/songs">Songs</NuxtLink>
      <NuxtLink to="/setlists">Set Lists</NuxtLink>
      <NuxtLink to="/history">History</NuxtLink>
      <NuxtLink to="/team">Team</NuxtLink>
    </div>
    <div v-if="status === 'authenticated'" class="self-start flex flex-row gap-4">
      <TeamMembersPending v-if="canManage" />
      <NuxtLink v-if="authData" to="/my/profile">
        <UserIcon :user-id="authData.id" large />
      </NuxtLink>
    </div>
    <div v-else>
      <NuxtLink to="/login">Sign In</NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
const { status, signOut, data: authData } = useAuth()

const { canManage } = useRole()
</script>
