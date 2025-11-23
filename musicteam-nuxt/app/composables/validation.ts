export function useInvalid(required: Ref[], optional: Ref[] = []) {
  const invalid = ref(true)
  const refs = [...required, ...optional]

  watch(
    refs,
    () => {
      nextTick(() => {
        for (const ref of required) {
          if (!ref.value || (Array.isArray(ref.value) && ref.value.length === 0)) {
            invalid.value = true
            return
          }
        }
        for (const frm of document.querySelectorAll(".frm-edit")) {
          if (!(frm as HTMLFormElement).checkValidity()) {
            invalid.value = true
            return
          }
        }
        invalid.value = false
      })
    },
    { deep: true, flush: "post" },
  )

  return invalid
}
