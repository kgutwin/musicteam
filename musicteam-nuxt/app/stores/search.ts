import type { SearchSongList } from "@/services/api"

export const useSearchStore = defineStore("search", () => {
  const query = ref<string>()
  const results = ref<SearchSongList>()

  return { query, results }
})
