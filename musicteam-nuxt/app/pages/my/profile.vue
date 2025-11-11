<template>
  <div>
    <Head><Title>My Profile - MusicTeam</Title></Head>

    <div class="flex flex-row w-full">
      <h1 class="grow">My Profile</h1>
      <div>
        <button class="btn-gray" @click="signOut({ callbackUrl: '/' })">Log Out</button>
      </div>
    </div>
    <div v-if="authData">
      <table class="tbl-definition">
        <tbody>
          <tr>
            <td>Name</td>
            <td>{{ authData.name }}</td>
          </tr>
          <tr>
            <td>Email</td>
            <td>{{ authData.email }}</td>
          </tr>
          <tr>
            <td>Profile picture</td>
            <td>
              <img
                v-if="authData.picture"
                :src="authData.picture"
                class="h-12 w-12 rounded-full"
                referrerpolicy="no-referrer"
              />
              <span v-else class="italic">No profile picture</span>
            </td>
          </tr>
          <tr>
            <td>System ID</td>
            <td>{{ authData.id }}</td>
          </tr>
          <tr>
            <td>Role</td>
            <td>{{ authData.role }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <h2 class="mt-8">API Access</h2>
    <div>
      <a href="/swagger-ui/index.html" class="text-blue-500 hover:underline">
        OpenAPI documentation and live explorer
      </a>
    </div>
    <UserGenerateApikey v-if="authData" :user-id="authData.id" />
  </div>
</template>

<script setup lang="ts">
import { useActiveSetlistStore } from "@/stores/setlists"

const { signOut, data: authData } = useAuth()

const activeStore = useActiveSetlistStore()

function logout() {
  activeStore.setlist = null

  signOut({ callbackUrl: "/" })
}
</script>
