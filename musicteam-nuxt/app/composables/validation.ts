export function useInvalid(required: Ref[], optional: Ref[] = []) {
  const invalid = ref(true)
  const refs = [...required, ...optional]

  watch(
    refs,
    () => {
      for (const ref of required) {
        if (!ref.value || (Array.isArray(ref.value) && ref.value.length === 0)) {
          console.log(ref)
          invalid.value = true
          return
        }
      }
      for (const frm of document.querySelectorAll(".frm-edit")) {
        if (!(frm as HTMLFormElement).checkValidity()) {
          console.log(frm)
          invalid.value = true
          return
        }
      }
      invalid.value = false
      console.log("good")
    },
    { deep: true, flush: "post" },
  )

  return invalid
}
