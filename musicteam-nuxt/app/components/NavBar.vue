<template>
  <div>
    <div class="nav-hamburger">
      <div class="grow font-extrabold italic ml-4">MusicTeam</div>

      <button @click="showMenu = true">
        <Icon name="solar:hamburger-menu-outline" />
      </button>
      <div
        v-if="showMenu"
        class="absolute h-screen w-screen z-10"
        @click="showMenu = false"
      />
    </div>
    <div
      class="nav-head"
      :class="{ 'max-sm:translate-x-full': !showMenu }"
      @click="showMenu = false"
    >
      <div class="nav-logo">
        <NuxtLink to="/">
          M<span class="hide-md">usic</span>T<span class="hide-md">eam</span>
        </NuxtLink>
      </div>

      <div class="nav-links">
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
  </div>
</template>

<script setup lang="ts">
const { status, signOut, data: authData } = useAuth()

const { canManage } = useRole()

const showMenu = ref(false)
</script>

<style>
.nav-hamburger {
  @apply sm:hidden text-2xl bg-slate-100 shadow flex flex-row items-baseline;

  & button {
    @apply rounded-lg bg-slate-100 shadow-md border border-blue-300 m-2 pt-1 px-2;
  }
}
.nav-head {
  @apply px-4 sm:px-8 py-4 text-xl bg-gradient-to-tr from-blue-300 to-sky-200;
  @apply flex flex-col sm:flex-row gap-4 items-baseline;

  @apply fixed top-0 right-0 sm:relative;
  @apply max-sm:h-screen z-20;
  @apply transition-transform sm:transition-none duration-300 ease-out;
}

.nav-logo {
  @apply text-3xl italic font-extrabold tracking-tight text-sky-700 bg-sky-100;
  @apply rounded-lg shadow-lg px-4 py-1 mr-4 md:mr-12;
}

.nav-links {
  @apply grow flex flex-col sm:flex-row gap-4 md:gap-8 font-semibold tracking-wide;
}
</style>
