<template>
  <div>
    <div class="flex flex-row w-full">
      <h1 class="grow">My Profile</h1>
      <div>
        <button class="btn-gray" @click="signOut({ callbackUrl: '/' })">Log Out</button>
      </div>
    </div>
    <div v-if="authData">
      <table class="tbl-definition">
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
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
const { signOut, data: authData } = useAuth()
</script>
