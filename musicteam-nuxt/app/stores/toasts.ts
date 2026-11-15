import { useToast, useModal } from "tailvue"

export const useToastStore = defineStore("toast", () => {
  const toast = useToast()
  return { toast }
})

export const useModalStore = defineStore("modal", () => {
  const modal = useModal()
  return { modal }
})
