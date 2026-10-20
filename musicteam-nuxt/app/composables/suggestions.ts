import { useTaglistStore } from "@/stores/info"

export function useTagSuggestions() {
  const allTags = useTaglistStore()
  allTags.get()

  return (q: string) =>
    (allTags.data?.entries ?? [])
      .map((entry) => entry.entry)
      .filter((tag) => tag.toLowerCase().startsWith(q.toLowerCase()))
}
