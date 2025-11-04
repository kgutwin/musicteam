// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  // devtools: { enabled: true },
  ssr: false,
  modules: [
    "@nuxtjs/tailwindcss",
    "@sidebase/nuxt-auth",
    "@pinia/nuxt",
    "@nuxt/icon",
    [
      "vite-plugin-version-mark/nuxt",
      { ifShortSHA: true, ifMeta: true, ifLog: true, ifGlobal: true },
    ],
  ],

  vue: {
    compilerOptions: {
      isCustomElement: (tag) => {
        if (tag === "pdfjs-viewer-element") return true
        return false
      },
    },
  },

  // for debugging
  // vite: { build: { minify: false } },
  sourcemap: true,

  nitro: {
    devProxy: {
      "/api": process.env.REMOTE_API
        ? {
            target: `https://${process.env.REMOTE_API}/api`,
            changeOrigin: true,
            headers: {
              "x-dev-host": "localhost:3000",
              "x-dev-proto": "http",
            },
          }
        : "http://127.0.0.1:8000",
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
          picture: "string",
          role: "string",
        },
      },
    },
  },
})
