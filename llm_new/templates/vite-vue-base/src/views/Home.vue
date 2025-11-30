<script setup>
</script>

<template>
  <div class="min-h-screen bg-black text-white">
    <!-- Navigation -->
    <nav class="sticky top-0 bg-black/70 backdrop-blur-lg z-50 border-b border-gray-800">
      <div class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
        <h3 class="text-xl font-bold">My Website</h3>
        <div class="flex gap-6">
          <router-link to="/" class="text-white hover:text-gray-300 transition">Home</router-link>
          <router-link to="/features" class="text-gray-400 hover:text-white transition">Features</router-link>
          <router-link to="/compare" class="text-gray-400 hover:text-white transition">Compare</router-link>
          <router-link to="/pricing" class="text-gray-400 hover:text-white transition">Pricing</router-link>
        </div>
        <button class="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-full transition">
          Get Started
        </button>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="relative h-screen flex items-center justify-center overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-br from-blue-900/20 to-purple-900/20"></div>
      <div class="relative z-10 text-center px-4">
        <h1 class="text-6xl md:text-8xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-purple-400 text-transparent bg-clip-text">
          Welcome
        </h1>
        <p class="text-xl md:text-2xl text-gray-300 mb-8">
          Build your dream website with AI
        </p>
        <button class="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-lg rounded-full transition">
          Start Building
        </button>
      </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-gray-800 py-8 text-center text-gray-500">
      <p>© 2025 My Website. All rights reserved.</p>
    </footer>
  </div>
</template>

<style scoped>
</style>
