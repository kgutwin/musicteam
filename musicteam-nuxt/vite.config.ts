/**
 * This file is only for supporting component-level testing in Cypress.
 */

import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"

export default defineConfig({ plugins: [vue()] })
