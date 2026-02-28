<template>
  <div class="ping-bar" />
</template>

<style>
.ping-bar {
  @apply fixed top-0 left-0 h-1 w-full bg-blue-500 z-40;
  animation: progressbar 30s cubic-bezier(0.21, 0.44, 0.95, 0.76);
}

@keyframes progressbar {
  from {
    transform: scaleX(0.1);
  }
  to {
    transform: scaleX(1);
  }
}
</style>
