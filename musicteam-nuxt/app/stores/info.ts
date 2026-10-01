import { api } from "@/services"
import { createStoreState, createParamStoreState } from "."

export const useAuthorlistStore = defineStore(
  "authorlist",
  createStoreState(async () => await api.info.listAuthors()),
)

export const useTaglistStore = defineStore(
  "taglist",
  createStoreState(async () => await api.info.listTags()),
)

export const useTagByResourcelistStore = defineStore(
  "tagbyresourcelist",
  createParamStoreState(
    async (params: { resourceType: string }) =>
      await api.info.listTagsByResourceType(params.resourceType),
  ),
)
