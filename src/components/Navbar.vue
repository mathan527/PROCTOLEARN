<template>
  <nav class="bg-white shadow">
    <div class="max-w-7xl mx-auto px-8 py-4 flex justify-between items-center">
      <router-link to="/" class="text-2xl font-bold text-primary">
        CauchyMentor
      </router-link>
      
      <div class="flex items-center gap-6">
        <router-link v-if="authStore.isAuthenticated" to="/course-generator" class="text-gray-600 hover:text-primary font-medium">
          🎓 AI Courses
        </router-link>
        <router-link v-if="authStore.isAuthenticated" to="/profile" class="text-gray-600 hover:text-primary">
          Profile
        </router-link>
        <button v-if="authStore.isAuthenticated" @click="logout" class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600">
          Logout
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const logout = () => {
  authStore.logout()
  router.push('/')
}
</script>
