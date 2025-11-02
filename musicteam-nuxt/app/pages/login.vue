<template>
  <div class="mx-auto max-w-[480px] rounded-xl border shadow-lg p-8">
    <Head><Title>Login - MusicTeam</Title></Head>

    <h1 class="w-full text-center">Sign In to MusicTeam</h1>
    <div v-if="signingIn" class="text-center">
      <Icon name="svg-spinners:270-ring-with-bg" size="32" />
    </div>
    <div v-else class="mt-12">
      <a
        href="/api/auth/google"
        class="btn-gray block text-center !p-2"
        @click="signingIn = true"
      >
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

const signingIn = ref<boolean>(!!route?.query?.complete)

watchEffect(() => {
  if (route?.query?.complete) {
    signingIn.value = true
    console.log("signing in")
    signIn({}, { redirect: true, callbackUrl: "/" })
  }
})
</script>
