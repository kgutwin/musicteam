import { defineConfig } from "cypress"

export default defineConfig({
  projectId: "j42dji",
  viewportWidth: 1025,
  e2e: {
    baseUrl: "http://localhost:3000",
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
})
