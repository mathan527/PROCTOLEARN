<template>
  <div class="min-h-screen bg-light">
    <!-- Header -->
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-8 py-6">
        <h1 class="text-3xl font-bold text-primary">Admin Panel</h1>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-8 py-12">
      <!-- Tabs -->
      <div class="flex gap-4 mb-8 border-b">
        <button @click="activeTab = 'users'" :class="activeTab === 'users' ? 'border-b-2 border-primary text-primary' : 'text-gray-600'" class="px-4 py-2 font-semibold">
          Users
        </button>
        <button @click="activeTab = 'logs'" :class="activeTab === 'logs' ? 'border-b-2 border-primary text-primary' : 'text-gray-600'" class="px-4 py-2 font-semibold">
          System Logs
        </button>
        <button @click="activeTab = 'consent'" :class="activeTab === 'consent' ? 'border-b-2 border-primary text-primary' : 'text-gray-600'" class="px-4 py-2 font-semibold">
          Consent Tracking
        </button>
      </div>

      <!-- Users Tab -->
      <div v-if="activeTab === 'users'" class="card">
        <h2 class="text-2xl font-bold mb-6">User Management</h2>
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-100">
              <tr>
                <th class="px-6 py-3 text-left font-semibold">Name</th>
                <th class="px-6 py-3 text-left font-semibold">Email</th>
                <th class="px-6 py-3 text-left font-semibold">Role</th>
                <th class="px-6 py-3 text-left font-semibold">Status</th>
                <th class="px-6 py-3 text-left font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id" class="border-b hover:bg-gray-50">
                <td class="px-6 py-3">{{ user.name }}</td>
                <td class="px-6 py-3">{{ user.email }}</td>
                <td class="px-6 py-3">
                  <span :class="user.role === 'teacher' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'" class="px-3 py-1 rounded-full text-sm font-semibold">
                    {{ user.role }}
                  </span>
                </td>
                <td class="px-6 py-3">
                  <span :class="user.active ? 'text-green-600' : 'text-red-600'" class="font-semibold">{{ user.active ? 'Active' : 'Inactive' }}</span>
                </td>
                <td class="px-6 py-3">
                  <button class="text-blue-600 hover:underline mr-4">Edit</button>
                  <button class="text-red-600 hover:underline">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Logs Tab -->
      <div v-if="activeTab === 'logs'" class="card">
        <h2 class="text-2xl font-bold mb-6">System Logs</h2>
        <div class="space-y-3">
          <div v-for="log in systemLogs" :key="log.id" class="p-4 bg-gray-50 rounded-lg border-l-4" :class="log.level === 'error' ? 'border-red-500' : 'border-blue-500'">
            <div class="flex justify-between items-start">
              <div>
                <p class="font-semibold">{{ log.message }}</p>
                <p class="text-sm text-gray-600">{{ log.timestamp }}</p>
              </div>
              <span :class="log.level === 'error' ? 'bg-red-100 text-red-800' : 'bg-blue-100 text-blue-800'" class="px-3 py-1 rounded text-sm font-semibold">
                {{ log.level }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Consent Tab -->
      <div v-if="activeTab === 'consent'" class="card">
        <h2 class="text-2xl font-bold mb-6">Consent Tracking</h2>
        <div class="space-y-4">
          <div v-for="consent in consentRecords" :key="consent.id" class="p-4 bg-gray-50 rounded-lg">
            <div class="flex justify-between items-start">
              <div>
                <p class="font-semibold">{{ consent.user }}</p>
                <p class="text-sm text-gray-600">{{ consent.type }}</p>
                <p class="text-xs text-gray-500 mt-1">{{ consent.date }}</p>
              </div>
              <span :class="consent.status === 'granted' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'" class="px-3 py-1 rounded text-sm font-semibold">
                {{ consent.status }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeTab = ref('users')

const users = ref([
  { id: 1, name: 'John Doe', email: 'john@example.com', role: 'student', active: true },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'teacher', active: true },
  { id: 3, name: 'Bob Johnson', email: 'bob@example.com', role: 'student', active: false }
])

const systemLogs = ref([
  { id: 1, message: 'User login successful', level: 'info', timestamp: '2024-01-20 10:30 AM' },
  { id: 2, message: 'Test submission failed', level: 'error', timestamp: '2024-01-20 10:25 AM' },
  { id: 3, message: 'Proctoring session started', level: 'info', timestamp: '2024-01-20 10:20 AM' }
])

const consentRecords = ref([
  { id: 1, user: 'John Doe', type: 'Camera Access', status: 'granted', date: '2024-01-20' },
  { id: 2, user: 'Jane Smith', type: 'Microphone Access', status: 'granted', date: '2024-01-20' },
  { id: 3, user: 'Bob Johnson', type: 'Screen Recording', status: 'pending', date: '2024-01-20' }
])
</script>
