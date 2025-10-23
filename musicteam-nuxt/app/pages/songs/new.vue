<template>
  <div>
    <h1>New Song</h1>
    <form class="frm-edit">
      <label>
        Title
        <input v-model="inputTitle" class="inp-text" />
      </label>

      <label>
        Authors
        <input v-model="inputAuthors" class="inp-text" />
      </label>

      <label>
        CCLI Number
        <input v-model="inputCcliNum" class="inp-text" />
      </label>

      <label>
        Tags
        <input v-model="inputTags" class="inp-text" />
      </label>

      <button class="btn-gray" @click="save">New Song</button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { api } from "@/services"

const inputTitle = ref<string>()
const inputAuthors = ref<string>()
const inputCcliNum = ref<string>()
const inputTags = ref<string>()

async function save() {
  const title = inputTitle.value
  const authors = (inputAuthors.value ?? "").split(/\s+/)
  const ccliNum = Number.isNaN(parseInt(inputCcliNum.value ?? ""))
    ? null
    : parseInt(inputCcliNum.value!)
  const tags = (inputTags.value ?? "").split(/\s+/)

  if (!title) return

  await api.songs.newSong({
    title,
    authors,
    ccli_num: ccliNum,
    tags,
  })

  await navigateTo({ path: "/songs" })
}
</script>
