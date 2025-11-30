export default defineNuxtRouteMiddleware((to) => {
  if (
    to.name &&
    ["login", "index", "pending", "my-profile"].includes(to.name as string)
  )
    return

  const { canView } = useRole()
  if (!canView) {
    return navigateTo("/pending")
  }
})
