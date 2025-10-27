import { api } from "@/services"
import { createStoreState, createParamStoreState } from "."

export const useUserlistStore = defineStore(
  "userlist",
  createStoreState(async () => await api.users.listUsers()),
)

export const useUserStore = defineStore(
  "user",
  createParamStoreState(
    async (params: { userId: string }) => await api.users.getUser(params.userId),
  ),
)
