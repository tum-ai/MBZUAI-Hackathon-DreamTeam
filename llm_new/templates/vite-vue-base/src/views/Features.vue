<script setup>
</script>

<template>
  <div class="min-h-screen bg-black text-white">
    <!-- Navigation -->
    <nav class="sticky top-0 bg-black/70 backdrop-blur-lg z-50 border-b border-gray-800">
      <div class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
        <h3 class="text-xl font-bold">My Website</h3>
        <div class="flex gap-6">
          <router-link to="/" class="text-gray-400 hover:text-white transition">Home</router-link>
          <router-link to="/features" class="text-white hover:text-gray-300 transition">Features</router-link>
          <router-link to="/compare" class="text-gray-400 hover:text-white transition">Compare</router-link>
          <router-link to="/pricing" class="text-gray-400 hover:text-white transition">Pricing</router-link>
        </div>
        <button class="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-full transition">
          Get Started
        </button>
      </div>
    </nav>

    <!-- Content -->
    <section class="max-w-6xl mx-auto px-6 py-20">
      <h1 class="text-5xl font-bold mb-12">Features</h1>
      
      <div class="grid md:grid-cols-3 gap-8">
        <div class="p-6 border border-gray-800 rounded-lg hover:border-gray-700 transition">
          <h3 class="text-2xl font-bold mb-4">Fast</h3>
          <p class="text-gray-400">Lightning-fast performance with modern tech</p>
        </div>
        
        <div class="p-6 border border-gray-800 rounded-lg hover:border-gray-700 transition">
          <h3 class="text-2xl font-bold mb-4">Secure</h3>
          <p class="text-gray-400">Enterprise-grade security built-in</p>
        </div>
        
        <div class="p-6 border border-gray-800 rounded-lg hover:border-gray-700 transition">
          <h3 class="text-2xl font-bold mb-4">Scalable</h3>
          <p class="text-gray-400">Grows with your business needs</p>
        </div>
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
