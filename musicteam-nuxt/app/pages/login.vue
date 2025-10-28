<template>
  <div class="mx-auto max-w-[480px] rounded-xl border shadow-lg p-8">
    <h1 class="w-full text-center">Sign In to MusicTeam</h1>
    <div class="mt-12">
      <a href="/api/auth/google" class="btn-gray block text-center !p-2">
        <Icon name="logos:google-icon" class="mr-4" />
        Sign in with Google
      </a>
    </div>
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
