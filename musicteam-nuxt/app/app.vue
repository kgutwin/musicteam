<template>
  <div class="page-grid page-grid-sidebar-open">
    <NavBar class="col-span-2" />

    <div class="container mx-auto p-8">
      <NuxtPage />
    </div>

    <SetlistSidebar class="row-span-2" />

    <Footer />
  </div>
</template>

<style>
.page-grid {
  @apply min-h-screen grid grid-cols-2 grid-rows-[auto_minmax(15rem,1fr)_auto];
}
.page-grid-sidebar-open {
  @apply grid-cols-[minmax(15rem,1fr)_auto];
}
</style>
