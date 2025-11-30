import type { User } from "@/services/api"

export type UserRole = User["role"]

export function useRole() {
  const { status, data } = useAuth()

  const authn = status.value === "authenticated"
  const role = data.value?.role as UserRole | undefined

  function hasRole(q: UserRole) {
    if (role === undefined) return false

    const roleSeq: UserRole[] = [
      "admin",
      "manager",
      "leader",
      "viewer",
      "pending",
      "inactive",
    ]
    return roleSeq.indexOf(role) <= roleSeq.indexOf(q)
  }

  return {
    role,
    hasRole,
    canView: authn && hasRole("viewer"),
    canEdit: authn && hasRole("leader"),
    canLead: authn && hasRole("leader"),
    canManage: authn && hasRole("manager"),
    canAdmin: authn && hasRole("admin"),
    async mustHave(role: UserRole, whenCannot: string) {
      if (!(authn && hasRole(role))) {
        await navigateTo(whenCannot)
      }
    },
  }
}
