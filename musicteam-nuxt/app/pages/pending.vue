<template>
  <div>
    <Head><Title>Pending User - MusicTeam</Title></Head>

    <template v-if="role === 'inactive'">
      <h1>Welcome back!</h1>
      <p class="mt-8">
        Your account here has been deactivated, so you can't currently access the
        resources of this team. If you'd like to rejoin, contact the team's managers and
        we'll get you reactivated. Thanks for your interest!
      </p>
    </template>
    <template v-else>
      <h1>Hang tight...</h1>
      <p class="mt-8">
        Thanks for signing in to MusicTeam. One of the team's managers will need to
        approve your membership and give you the correct role on the team. Let us know
        via email or text that you've signed in, and we'll get you set up!
      </p>
    </template>
  </div>
</template>

<script setup lang="ts">
const { role } = useRole()
</script>
