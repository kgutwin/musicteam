<template>
  <div class="page-grid">
    <NavBar />

    <div class="container mx-auto p-8">
      <NuxtPage />
    </div>

    <Footer />
  </div>
</template>

<style>
.page-grid {
  @apply min-h-screen grid grid-cols-1 grid-rows-[auto_minmax(15rem,1fr)_auto];
}
</style>
