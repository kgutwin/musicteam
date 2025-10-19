// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  // devtools: { enabled: true },
  ssr: false,
  modules: ["@nuxtjs/tailwindcss", "@sidebase/nuxt-auth"],

  // routeRules: {
  //   "/api/**": { proxy: "http://127.0.0.1:8000/**" },
  // },
  nitro: {
    devProxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },

  auth: {
    isEnabled: true,
    baseURL: "/api/auth",

    // protect all pages by default
    globalAppMiddleware: true,

    provider: {
      // type: "authjs",
      // addDefaultCallbackUrl: true,
      type: "local",
      endpoints: {
        signIn: { path: "/login", method: "post" },
        signOut: { path: "/logout", method: "post" },
        signUp: false,
        getSession: { path: "/session", method: "get" },
      },
      pages: {
        login: "/login",
      },
      session: {
        dataType: {
          id: "string",
          name: "string",
          email: "string",
          role: "string",
        },
      },
    },
  },
})
