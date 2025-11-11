<template>
  <table class="tbl-definition">
    <tbody>
      <tr>
        <td>API Key</td>
        <td v-if="resp">{{ resp.api_key }}</td>
        <td v-else>
          <span class="italic mr-8">Not shown for security</span>
          <button class="btn-gray" @click="generate">Generate new API key</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
import { api } from "@/services"
import type { UserApikey } from "@/services/api"

const props = defineProps<{ userId: string }>()

const resp = ref<UserApikey>()

async function generate() {
  useToaster(async () => {
    const rv = await api.users.createUserApikey(props.userId)
    resp.value = rv.data
  })
}
</script>
