import { api } from "@/services"
import { createStoreState } from "."

export const useUsersStore = defineStore(
  "users",
  createStoreState(async () => await api.users.listUsers()),
)
