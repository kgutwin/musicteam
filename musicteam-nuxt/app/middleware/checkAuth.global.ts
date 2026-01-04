export default defineNuxtRouteMiddleware((to) => {
  if (
    to.name &&
    ["login", "index", "pending", "my-profile"].includes(to.name as string)
  )
    return

  const { role, canView } = useRole()
  if (role && !canView) {
    return navigateTo("/pending")
  }
})
