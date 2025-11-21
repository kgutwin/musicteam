<template>
  <div class="mx-auto max-w-[480px] rounded-xl border shadow-lg p-8">
    <Head><Title>Login - MusicTeam</Title></Head>

    <h1 class="w-full text-center">Sign In to MusicTeam</h1>
    <div class="text-center my-6" :class="signingIn ? '' : 'invisible'">
      <Icon name="svg-spinners:3-dots-fade" size="32" />
    </div>
    <div v-if="!signingIn">
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
const callbackUrl = ref<string | null>(sessionStorage.getItem("callbackUrl"))

if (route?.query?.redirect) {
  callbackUrl.value = route.query.redirect as string
  sessionStorage.setItem("callbackUrl", callbackUrl.value!)
}

watchEffect(() => {
  if (route?.query?.complete) {
    signingIn.value = true
    console.log("signing in")
    sessionStorage.removeItem("callbackUrl")
    signIn({}, { redirect: true, callbackUrl: callbackUrl.value ?? "/" })
  }
})
</script>
