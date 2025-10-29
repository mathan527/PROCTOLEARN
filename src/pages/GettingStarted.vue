<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
    <header class="bg-white shadow-md">
      <div class="max-w-7xl mx-auto px-8 py-4 flex justify-between items-center">
        <router-link to="/" class="text-2xl font-bold text-indigo-600">
          🎓 CauchyMentor
        </router-link>
        <div class="flex gap-4">
          <router-link 
            v-if="authStore.user?.role === 'student'"
            to="/student/dashboard"
            class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Go to Dashboard
          </router-link>
          <router-link 
            v-if="authStore.user?.role === 'teacher'"
            to="/teacher/dashboard"
            class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Go to Dashboard
          </router-link>
        </div>
      </div>
    </header>

    <div class="max-w-5xl mx-auto px-8 py-12">
      <div class="text-center mb-12">
        <h1 class="text-5xl font-bold text-gray-900 mb-4">🚀 Getting Started</h1>
        <p class="text-xl text-gray-600">Your AI-Powered Learning Platform</p>
      </div>

      <!-- Quick Start Steps -->
      <div class="bg-white rounded-2xl shadow-xl p-8 mb-8">
        <h2 class="text-3xl font-bold text-gray-900 mb-6">📚 How to Use CauchyMentor</h2>
        
        <div class="space-y-8">
          <!-- Step 1 -->
          <div class="flex gap-6">
            <div class="flex-shrink-0 w-12 h-12 bg-indigo-600 text-white rounded-full flex items-center justify-center text-xl font-bold">
              1
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900 mb-2">Generate AI Course</h3>
              <p class="text-gray-600 mb-3">
                Click <strong>"🎓 AI Courses"</strong> in the navigation menu. Enter any topic you want to learn (e.g., "Machine Learning", "Calculus", "Web Development").
              </p>
              <ul class="list-disc list-inside text-gray-600 space-y-1 ml-4">
                <li>Choose duration (1-90 days)</li>
                <li>Select difficulty level (Beginner/Medium/Advanced)</li>
                <li>Pick learning style (Comprehensive/Practical/Theoretical/Fast-track)</li>
              </ul>
              <router-link to="/course-generator" class="inline-block mt-3 px-6 py-2 bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 font-medium">
                Start Learning →
              </router-link>
            </div>
          </div>

          <!-- Step 2 -->
          <div class="flex gap-6">
            <div class="flex-shrink-0 w-12 h-12 bg-green-600 text-white rounded-full flex items-center justify-center text-xl font-bold">
              2
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900 mb-2">Study Daily Lessons</h3>
              <p class="text-gray-600 mb-3">
                Your course will be broken down into daily lessons with:
              </p>
              <ul class="list-disc list-inside text-gray-600 space-y-1 ml-4">
                <li>📖 Clear learning objectives</li>
                <li>📚 Detailed content and examples</li>
                <li>⏱️ Estimated time requirements</li>
                <li>🎯 Practice activities and resources</li>
              </ul>
            </div>
          </div>

          <!-- Step 3 -->
          <div class="flex gap-6">
            <div class="flex-shrink-0 w-12 h-12 bg-purple-600 text-white rounded-full flex items-center justify-center text-xl font-bold">
              3
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900 mb-2">Take AI-Generated Tests</h3>
              <p class="text-gray-600 mb-3">
                On assessment days (usually every 3-7 days), take proctored tests to verify your learning:
              </p>
              <ul class="list-disc list-inside text-gray-600 space-y-1 ml-4">
                <li>📝 AI generates questions based on covered topics</li>
                <li>📹 Camera proctoring ensures fair testing</li>
                <li>🔍 Face detection and tab monitoring</li>
                <li>✅ Instant feedback on your progress</li>
              </ul>
            </div>
          </div>

          <!-- Step 4 -->
          <div class="flex gap-6">
            <div class="flex-shrink-0 w-12 h-12 bg-orange-600 text-white rounded-full flex items-center justify-center text-xl font-bold">
              4
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900 mb-2">Track Your Progress</h3>
              <p class="text-gray-600">
                Complete the course day by day, passing assessments along the way. Your dashboard shows completed lessons, test scores, and overall progress.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Features -->
      <div class="grid md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white rounded-xl shadow-lg p-6">
          <div class="text-4xl mb-4">🤖</div>
          <h3 class="text-xl font-bold text-gray-900 mb-2">AI-Powered</h3>
          <p class="text-gray-600">Advanced AI generates personalized courses and assessments tailored to your needs.</p>
        </div>
        
        <div class="bg-white rounded-xl shadow-lg p-6">
          <div class="text-4xl mb-4">📹</div>
          <h3 class="text-xl font-bold text-gray-900 mb-2">Proctored Tests</h3>
          <p class="text-gray-600">Fair testing with camera monitoring, face detection, and tab switch detection.</p>
        </div>
        
        <div class="bg-white rounded-xl shadow-lg p-6">
          <div class="text-4xl mb-4">🎯</div>
          <h3 class="text-xl font-bold text-gray-900 mb-2">Structured Learning</h3>
          <p class="text-gray-600">Progressive daily lessons with clear objectives and practice activities.</p>
        </div>
      </div>

      <!-- Call to Action -->
      <div class="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl shadow-xl p-12 text-center text-white">
        <h2 class="text-3xl font-bold mb-4">Ready to Start Learning?</h2>
        <p class="text-xl mb-8 opacity-90">Generate your first AI course in seconds!</p>
        <router-link 
          to="/course-generator" 
          class="inline-block px-8 py-4 bg-white text-indigo-600 rounded-lg font-bold text-lg hover:bg-gray-100 transition shadow-lg"
        >
          🚀 Generate Course Now
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
</script>
