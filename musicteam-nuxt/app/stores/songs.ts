import { api } from "@/services"
import { createStoreState } from "."

export const useSongsStore = defineStore(
  "songs",
  createStoreState(async () => await api.songs.listSongs()),
)
