import { defineConfig } from "cypress"
import psList from "ps-list"

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
      on("task", {
        async killSemanticTasks() {
          const tasks = (await psList()).filter((task) =>
            task.cmd.includes("-m chalicelib.semantic"),
          )
          console.log(`found ${tasks.length} tasks to kill`)
          for (const task of tasks) {
            console.log(`killing ${task.pid}: ${task.cmd}`)
            process.kill(task.pid)
          }
          return tasks.length
        },
      })
    },
  },

  component: {
    devServer: {
      framework: "vue",
      bundler: "vite",
    },
  },
})
