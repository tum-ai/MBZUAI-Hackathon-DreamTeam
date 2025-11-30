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
          <router-link to="/features" class="text-gray-400 hover:text-white transition">Features</router-link>
          <router-link to="/compare" class="text-white hover:text-gray-300 transition">Compare</router-link>
          <router-link to="/pricing" class="text-gray-400 hover:text-white transition">Pricing</router-link>
        </div>
        <button class="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-full transition">
          Get Started
        </button>
      </div>
    </nav>

    <!-- Content -->
    <section class="max-w-6xl mx-auto px-6 py-20">
      <h1 class="text-5xl font-bold mb-12">Compare Plans</h1>
      
      <div class="overflow-x-auto">
        <table class="w-full border-collapse">
          <thead>
            <tr class="border-b border-gray-800">
              <th class="py-4 px-6 text-left">Feature</th>
              <th class="py-4 px-6 text-center">Basic</th>
              <th class="py-4 px-6 text-center">Pro</th>
              <th class="py-4 px-6 text-center">Enterprise</th>
            </tr>
          </thead>
          <tbody class="text-gray-400">
            <tr class="border-b border-gray-800">
              <td class="py-4 px-6">Users</td>
              <td class="py-4 px-6 text-center">1</td>
              <td class="py-4 px-6 text-center">10</td>
              <td class="py-4 px-6 text-center">Unlimited</td>
            </tr>
            <tr class="border-b border-gray-800">
              <td class="py-4 px-6">Storage</td>
              <td class="py-4 px-6 text-center">1GB</td>
              <td class="py-4 px-6 text-center">100GB</td>
              <td class="py-4 px-6 text-center">Unlimited</td>
            </tr>
            <tr class="border-b border-gray-800">
              <td class="py-4 px-6">Support</td>
              <td class="py-4 px-6 text-center">Email</td>
              <td class="py-4 px-6 text-center">Priority</td>
              <td class="py-4 px-6 text-center">24/7</td>
            </tr>
          </tbody>
        </table>
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
