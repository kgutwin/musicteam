<template>
  <div class="page-grid">
    <NavBar class="sm:col-span-2 order-0" />

    <div class="container mx-auto p-4 sm:p-8 order-2 sm:order-1">
      <slot />
    </div>

    <SetlistSidebar class="sm:row-span-2 order-1 sm:order-2" />

    <Footer class="order-3" />
  </div>
</template>

<style>
.page-grid {
  @apply min-h-screen grid grid-cols-1 sm:grid-cols-2 sm:grid-cols-[minmax(15rem,1fr)_auto];
  @apply grid-rows-[auto_auto_minmax(15rem,1fr)_auto];
  @apply sm:grid-rows-[auto_minmax(15rem,1fr)_auto];
}
</style>
