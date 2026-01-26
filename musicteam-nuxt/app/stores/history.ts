import { api } from "@/services"
import { createStoreState, createParamStoreState } from "."

export const useSongHistoryStore = defineStore(
  "songhistory",
  createParamStoreState(
    async (params: { songId: string }) =>
      await api.history.getSongHistory(params.songId),
  ),
)

export const useHistorySparklineStore = defineStore(
  "historysparkline",
  createStoreState(async () => await api.history.getHistorySparkline()),
)

export const useHistoryTopSongsStore = defineStore(
  "historytopsongs",
  createParamStoreState(
    async (params: { ranking: "alltime" | "recent" | "weighted" }) =>
      await api.history.getHistoryTopSongs({ ranking: params.ranking }),
  ),
)
