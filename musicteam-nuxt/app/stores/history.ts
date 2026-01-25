import { api } from "@/services"
import { createParamStoreState } from "."

export const useSongHistoryStore = defineStore(
  "songhistory",
  createParamStoreState(
    async (params: { songId: string }) =>
      await api.history.getSongHistory(params.songId),
  ),
)
