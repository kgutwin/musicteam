import { h, defineComponent, resolveComponent } from "vue"

export default defineComponent({
  props: {
    text: { type: String, default: "" },
  },

  setup(props: { text: string }) {
    const Icon = resolveComponent("Icon")

    const parts = computed(() => {
      const lines = []
      let hit
      for (let line of props.text.split(/\r?\n/)) {
        const rl = []
        while ((hit = line.match(/(.*?)<b>(.*?)<\/b>(.*)/s)) !== null) {
          if (hit[1]) rl.push(hit[1])
          if (hit[2]) rl.push(h("b", {}, hit[2]))
          line = hit[3]!
        }
        if (line) rl.push(line)
        lines.push(rl)
      }

      const rv = lines.flatMap((rl) => [
        ...rl,
        // h(Icon, { name: "ri:corner-down-left-line", class: "text-gray-300" }),
        " · ",
      ])
      rv.pop()
      return rv
    })
    return () => h("div", {}, parts.value)
  },
})
