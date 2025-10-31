import { useToast } from "tailvue"

export const useToastStore = defineStore("toast", () => {
  const toast = useToast()
  return { toast }
})
