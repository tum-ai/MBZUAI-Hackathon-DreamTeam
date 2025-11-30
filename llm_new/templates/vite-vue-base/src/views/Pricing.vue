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
          <router-link to="/compare" class="text-gray-400 hover:text-white transition">Compare</router-link>
          <router-link to="/pricing" class="text-white hover:text-gray-300 transition">Pricing</router-link>
        </div>
        <button class="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-full transition">
          Get Started
        </button>
      </div>
    </nav>

    <!-- Content -->
    <section class="max-w-6xl mx-auto px-6 py-20">
      <h1 class="text-5xl font-bold mb-4 text-center">Simple Pricing</h1>
      <p class="text-xl text-gray-400 mb-12 text-center">Choose the plan that's right for you</p>
      
      <div class="grid md:grid-cols-3 gap-8">
        <!-- Basic -->
        <div class="p-8 border border-gray-800 rounded-lg hover:border-blue-600 transition">
          <h3 class="text-2xl font-bold mb-2">Basic</h3>
          <p class="text-4xl font-bold mb-6">$9<span class="text-lg text-gray-400">/mo</span></p>
          <ul class="space-y-3 mb-8">
            <li class="flex items-center"><span class="mr-2">✓</span> 1 User</li>
            <li class="flex items-center"><span class="mr-2">✓</span> 1GB Storage</li>
            <li class="flex items-center"><span class="mr-2">✓</span> Email Support</li>
          </ul>
          <button class="w-full px-6 py-3 border border-gray-700 hover:bg-gray-900 rounded-full transition">
            Choose Plan
          </button>
        </div>
        
        <!-- Pro -->
        <div class="p-8 border-2 border-blue-600 rounded-lg relative">
          <div class="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-blue-600 px-4 py-1 rounded-full text-sm">
            Popular
          </div>
          <h3 class="text-2xl font-bold mb-2">Pro</h3>
          <p class="text-4xl font-bold mb-6">$29<span class="text-lg text-gray-400">/mo</span></p>
          <ul class="space-y-3 mb-8">
            <li class="flex items-center"><span class="mr-2">✓</span> 10 Users</li>
            <li class="flex items-center"><span class="mr-2">✓</span> 100GB Storage</li>
            <li class="flex items-center"><span class="mr-2">✓</span> Priority Support</li>
          </ul>
          <button class="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-full transition">
            Choose Plan
          </button>
        </div>
        
        <!-- Enterprise -->
        <div class="p-8 border border-gray-800 rounded-lg hover:border-blue-600 transition">
          <h3 class="text-2xl font-bold mb-2">Enterprise</h3>
          <p class="text-4xl font-bold mb-6">$99<span class="text-lg text-gray-400">/mo</span></p>
          <ul class="space-y-3 mb-8">
            <li class="flex items-center"><span class="mr-2">✓</span> Unlimited Users</li>
            <li class="flex items-center"><span class="mr-2">✓</span> Unlimited Storage</li>
            <li class="flex items-center"><span class="mr-2">✓</span> 24/7 Support</li>
          </ul>
          <button class="w-full px-6 py-3 border border-gray-700 hover:bg-gray-900 rounded-full transition">
            Choose Plan
          </button>
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
