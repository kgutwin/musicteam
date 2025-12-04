import { api } from "@/services"
import { createStoreState } from "."

export const useAuthorlistStore = defineStore(
  "authorlist",
  createStoreState(async () => await api.info.listAuthors()),
)

export const useTaglistStore = defineStore(
  "taglist",
  createStoreState(async () => await api.info.listTags()),
)
