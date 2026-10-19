import { defineConfig } from "cypress"

export default defineConfig({
  projectId: "j42dji",
  viewportWidth: 1025,
  video: true,
  // defaultCommandTimeout: 8000,

  retries: {
    runMode: 1,
  },

  e2e: {
    baseUrl: "http://localhost:3000",
    setupNodeEvents(on, config) {
      // tasks and such go here
    },
  },

  component: {
    devServer: {
      framework: "vue",
      bundler: "vite",
    },
  },
})
