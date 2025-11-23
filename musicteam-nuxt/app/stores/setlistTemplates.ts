import { api } from "@/services"
import { createStoreState, createParamStoreState } from "."

export const useSetlistTemplatelistStore = defineStore(
  "setlisttemplatelist",
  createStoreState(async () => await api.setlistTemplates.listSetlistTemplates()),
)

export const useSetlistTemplateStore = defineStore(
  "setlisttemplate",
  createParamStoreState(
    async (params: { templateId: string }) =>
      await api.setlistTemplates.getSetlistTemplate(params.templateId),
  ),
)

export const useSetlistTemplatePositionlistStore = defineStore(
  "setlisttemplatepositionlist",
  createParamStoreState(
    async (params: { templateId: string }) =>
      await api.setlistTemplates.listSetlistTemplatePositions(params.templateId),
  ),
)

export const useSetlistTemplateRefreshStore = defineStore(
  "setlisttemplateRefresh",
  createRefreshStoreState([
    useSetlistTemplatelistStore,
    useSetlistTemplateStore,
    useSetlistTemplatePositionlistStore,
  ]),
)
