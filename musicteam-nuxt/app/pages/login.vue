<template>
  <h2>Login</h2>
  <div>
    <a href="/api/auth/google" class="btn-gray"> Sign in with Google </a>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ auth: { unauthenticatedOnly: true, navigateAuthenticatedTo: "/" } })

const { signIn } = useAuth()
const route = useRoute()

watchEffect(() => {
  if (route?.query?.complete) {
    console.log("signing in")
    signIn({}, { redirect: true, callbackUrl: "/" })
  }
})
</script>
