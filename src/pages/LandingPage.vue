<template>
  <div class="min-h-screen bg-black text-white">
    <!-- Navigation -->
    <nav class="fixed top-0 w-full z-50 bg-white shadow-lg">
      <div class="max-w-7xl mx-auto px-8 py-4 flex justify-between items-center">
        <h1 class="text-3xl font-black text-black tracking-tight">
          Proto<span class="text-gray-600">Learn</span>
        </h1>
        <div class="flex gap-4">
          <router-link to="/login" class="px-6 py-2.5 text-black font-semibold hover:bg-gray-100 rounded-lg transition-all">
            Login
          </router-link>
          <router-link to="/register" class="px-6 py-2.5 bg-black text-white font-semibold rounded-lg hover:bg-gray-800 transition-all shadow-md">
            Get Started
          </router-link>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="pt-32 pb-20 px-8">
      <div class="max-w-6xl mx-auto">
        <!-- Badge -->
        <div class="flex justify-center mb-8">
          <span class="px-4 py-2 bg-white bg-opacity-10 backdrop-blur-sm border border-white border-opacity-20 rounded-full text-sm font-semibold text-gray-300">
            🚀 Next Generation Proctoring Platform
          </span>
        </div>

        <!-- Main Heading -->
        <h2 class="text-6xl md:text-7xl font-black text-center mb-6 leading-tight">
          AI-Powered
          <span class="block bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
            Proctoring
          </span>
        </h2>
        
        <p class="text-xl text-gray-400 text-center mb-12 max-w-3xl mx-auto leading-relaxed">
          ProtoLearn combines cutting-edge machine learning with secure real-time monitoring 
          to revolutionize online examination integrity.
        </p>
        
        <!-- CTA Buttons -->
        <div class="flex gap-6 justify-center mb-20">
          <router-link to="/login?role=student" 
            class="group px-8 py-4 bg-white text-black font-bold rounded-xl hover:bg-gray-100 transition-all text-lg shadow-2xl hover:shadow-white/20 hover:scale-105 transform">
            <span class="flex items-center gap-2">
              Login as Student
              <svg class="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
              </svg>
            </span>
          </router-link>
          <router-link to="/login?role=teacher" 
            class="group px-8 py-4 bg-transparent text-white font-bold rounded-xl border-2 border-white hover:bg-white hover:text-black transition-all text-lg hover:scale-105 transform">
            <span class="flex items-center gap-2">
              Login as Teacher
              <svg class="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
              </svg>
            </span>
          </router-link>
        </div>

        <!-- Stats -->
        <div class="grid grid-cols-3 gap-8 max-w-3xl mx-auto mb-20 text-center">
          <div class="group">
            <div class="text-4xl font-black mb-2 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              4+
            </div>
            <div class="text-sm text-gray-500 font-semibold uppercase tracking-wide">AI Models</div>
          </div>
          <div class="group">
            <div class="text-4xl font-black mb-2 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              99.9%
            </div>
            <div class="text-sm text-gray-500 font-semibold uppercase tracking-wide">Accuracy</div>
          </div>
          <div class="group">
            <div class="text-4xl font-black mb-2 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              Real-time
            </div>
            <div class="text-sm text-gray-500 font-semibold uppercase tracking-wide">Monitoring</div>
          </div>
        </div>

        <!-- Features Grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <!-- Feature 1 -->
          <div class="group relative p-8 bg-gradient-to-br from-white/5 to-white/10 backdrop-blur-sm rounded-2xl border border-white/10 hover:border-white/30 transition-all hover:scale-105 transform">
            <div class="absolute inset-0 bg-gradient-to-br from-blue-500/0 to-purple-500/0 group-hover:from-blue-500/10 group-hover:to-purple-500/10 rounded-2xl transition-all"></div>
            <div class="relative">
              <div class="text-5xl mb-4">🎯</div>
              <h3 class="text-2xl font-bold mb-4">ML Detection</h3>
              <p class="text-gray-400 leading-relaxed">
                4 AI models with retry mechanism and fallback detection for comprehensive monitoring.
              </p>
              <div class="mt-6 flex gap-2 flex-wrap">
                <span class="px-3 py-1 bg-white/10 rounded-full text-xs font-semibold">MediaPipe</span>
                <span class="px-3 py-1 bg-white/10 rounded-full text-xs font-semibold">BlazeFace</span>
                <span class="px-3 py-1 bg-white/10 rounded-full text-xs font-semibold">FaceMesh</span>
                <span class="px-3 py-1 bg-white/10 rounded-full text-xs font-semibold">COCO-SSD</span>
              </div>
            </div>
          </div>

          <!-- Feature 2 -->
          <div class="group relative p-8 bg-gradient-to-br from-white/5 to-white/10 backdrop-blur-sm rounded-2xl border border-white/10 hover:border-white/30 transition-all hover:scale-105 transform">
            <div class="absolute inset-0 bg-gradient-to-br from-green-500/0 to-teal-500/0 group-hover:from-green-500/10 group-hover:to-teal-500/10 rounded-2xl transition-all"></div>
            <div class="relative">
              <div class="text-5xl mb-4">🔒</div>
              <h3 class="text-2xl font-bold mb-4">Real-time Proctoring</h3>
              <p class="text-gray-400 leading-relaxed">
                WebRTC video streaming, face detection, and fullscreen enforcement for exam integrity.
              </p>
              <div class="mt-6 flex gap-2 flex-wrap">
                <span class="px-3 py-1 bg-white/10 rounded-full text-xs font-semibold">WebRTC P2P</span>
                <span class="px-3 py-1 bg-white/10 rounded-full text-xs font-semibold">Fullscreen Lock</span>
                <span class="px-3 py-1 bg-white/10 rounded-full text-xs font-semibold">Tab Detection</span>
              </div>
            </div>
          </div>

          <!-- Feature 3 -->
          <div class="group relative p-8 bg-gradient-to-br from-white/5 to-white/10 backdrop-blur-sm rounded-2xl border border-white/10 hover:border-white/30 transition-all hover:scale-105 transform">
            <div class="absolute inset-0 bg-gradient-to-br from-orange-500/0 to-red-500/0 group-hover:from-orange-500/10 group-hover:to-red-500/10 rounded-2xl transition-all"></div>
            <div class="relative">
              <div class="text-5xl mb-4">📊</div>
              <h3 class="text-2xl font-bold mb-4">Complete Analytics</h3>
              <p class="text-gray-400 leading-relaxed">
                Track violations, export results, and monitor students in real-time from dashboard.
              </p>
              <div class="mt-6 flex gap-2 flex-wrap">
                <span class="px-3 py-1 bg-white/10 rounded-full text-xs font-semibold">CSV Export</span>
                <span class="px-3 py-1 bg-white/10 rounded-full text-xs font-semibold">Live Monitor</span>
                <span class="px-3 py-1 bg-white/10 rounded-full text-xs font-semibold">Violations</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-white/10 py-8 mt-20">
      <div class="max-w-6xl mx-auto px-8 text-center text-gray-500">
        <p class="text-sm">&copy; 2025 ProtoLearn. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
// ProtoLearn Landing page
</script>
