<template>
  <div>
    <input type="file" accept="audio/*" @change="selectFile" />
    <div>{{ progress }} - {{ objectId }}</div>

    <!--
    <div v-if="false" class="overflow-auto max-w-full">
      <AVWaveform
        v-if="audioUrl"
        :src="audioUrl"
        :canv-width="1400"
        noplayed-line-color="blue"
      />
    </div>
    -->
  </div>
</template>

<script setup lang="ts">
import { AVWaveform } from "vue-audio-visual"
import { flacEncode } from "./ingest"

// const audioUrl = ref<string>()
const objectId = ref<string>()
const progress = ref<number>()

async function selectFile(event: any) {
  const file = event.target?.files?.[0] as File | undefined
  if (file) {
    // const fileURL = window.URL.createObjectURL(file)
    // audioUrl.value = fileURL
    objectId.value = await flacEncode(file, (p) => {
      progress.value = p
    })
  }
}

// plan
// - upload file as above
// - Set start and end points
// - Pick what song you want to assign it to
// - Read WAV data (somehow)
//   - Feed to FLAC encoder
//   - save as object
//   - create media reference ...
// - repeat

// need
// - waveform view
//   - select start and end
//   - get wav data between points

// alternate plan
// - select file, load into player
// - use player audio interface to do FLAC conversion
// - upload entire FLAC file directly as a media attachment to the setlist
// - then, with the file reloaded, interface now allows setting 'bookmarks'
//   - a bookmark gets saved as a media attachment on the associated song version
//   - that is rendered as loading the whole recording inside the song media list,
//     then skipping to the bookmark
//     - a dedicated button is needed to restore the position to the original bookmark
//   - why not just link them over to the setlist? because they need to easily be
//     able to see the lyrics/chords/etc... after all, that's why they're there in
//     the first place

// tradeoffs
// - alternate plan is..
//   - easier on end users (just set bookmarks, or no bookmarks :shrug:)
//   - doesn't concern itself with excess recording (so what, who cares)
//   - doesn't auto-stop at the end of listening to a song
//   - probably puts excess load on users who innocently open the media panel
//   - also makes subsequent setlist media more confusing (how many 2+hr recordings
//     can we fit into one tiny media panel??)
// - original plan is..
//   - trimmer -- only keep what we care about, individual song recordings
//   - easier to navigate long-term
//   - more effort in the short term (where does this song end, exactly?)
//   - if we don't save the full recording, then maybe we're losing something that we
//     wanted to save ?
</script>
