<template>
  <h2>Login</h2>
  <div>
    <button class="btn-gray" @click="signIn('google', { callbackUrl: '/songs' })">
      Sign in with Google
    </button>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ auth: { unauthenticatedOnly: true, navigateAuthenticatedTo: "/" } })

const { signIn } = useAuth()
</script>
