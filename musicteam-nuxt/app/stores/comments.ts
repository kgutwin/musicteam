import { api } from "@/services"
import { createParamStoreState, createRefreshStoreState } from "."

export const useCommentlistStore = defineStore(
  "commentlist",
  createParamStoreState(
    async (params: { resourceId: string }) =>
      await api.comments.listComments(params.resourceId),
  ),
)

export const useCommentRefreshStore = defineStore(
  "commentRefresh",
  createRefreshStoreState([useCommentlistStore]),
)
