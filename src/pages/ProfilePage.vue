<template>
  <div class="min-h-screen bg-light">
    <!-- Header -->
    <header class="bg-white shadow">
      <div class="max-w-4xl mx-auto px-8 py-6">
        <h1 class="text-3xl font-bold text-primary">My Profile</h1>
      </div>
    </header>

    <main class="max-w-4xl mx-auto px-8 py-12">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- Profile Info -->
        <div class="md:col-span-2">
          <div class="card">
            <h2 class="text-2xl font-bold mb-6">Personal Information</h2>
            
            <form @submit.prevent="saveProfile" class="space-y-6">
              <div>
                <label class="block text-sm font-semibold mb-2">Full Name</label>
                <input v-model="profile.name" type="text" class="input-field" />
              </div>

              <div>
                <label class="block text-sm font-semibold mb-2">Email</label>
                <input v-model="profile.email" type="email" class="input-field" />
              </div>

              <div>
                <label class="block text-sm font-semibold mb-2">Current Password</label>
                <input v-model="profile.currentPassword" type="password" class="input-field" />
              </div>

              <div>
                <label class="block text-sm font-semibold mb-2">New Password (optional)</label>
                <input v-model="profile.newPassword" type="password" class="input-field" />
              </div>

              <div>
                <label class="flex items-center gap-3">
                  <input v-model="profile.proctoringConsent" type="checkbox" class="w-5 h-5" />
                  <span class="font-semibold">I consent to proctoring and monitoring</span>
                </label>
              </div>

              <button type="submit" class="btn-primary">
                Save Changes
              </button>
            </form>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Test History -->
          <div class="card">
            <h3 class="text-xl font-bold mb-4">Test History</h3>
            <div class="space-y-3">
              <div v-for="test in testHistory" :key="test.id" class="p-3 bg-gray-50 rounded">
                <p class="font-semibold text-sm">{{ test.title }}</p>
                <p class="text-xs text-gray-600">Score: {{ test.score }}%</p>
                <p class="text-xs text-gray-500">{{ test.date }}</p>
              </div>
            </div>
          </div>

          <!-- Account Stats -->
          <div class="card">
            <h3 class="text-xl font-bold mb-4">Account Stats</h3>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600">Member Since</span>
                <span class="font-semibold">Jan 2024</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Tests Taken</span>
                <span class="font-semibold">12</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Avg Score</span>
                <span class="font-semibold">82%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const profile = ref({
  name: 'John Doe',
  email: 'john@example.com',
  currentPassword: '',
  newPassword: '',
  proctoringConsent: true
})

const testHistory = ref([
  { id: 1, title: 'Calculus Basics', score: 85, date: '2024-01-15' },
  { id: 2, title: 'Linear Algebra', score: 78, date: '2024-01-10' }
])

const saveProfile = () => {
  // TODO: Send profile update to backend
  console.log('Profile saved:', profile.value)
  alert('Profile updated successfully!')
}
</script>
