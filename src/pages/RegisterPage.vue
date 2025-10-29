<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-blue-100 px-4">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-xl p-8">
      <h2 class="text-3xl font-bold mb-2 text-center text-gray-900">Create Account</h2>
      <p class="text-center text-gray-600 mb-8">Join ProctoLearn today</p>
      
      <form @submit.prevent="handleRegister" class="space-y-4">
        <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {{ error }}
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
          <input 
            v-model="fullName" 
            type="text" 
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
            placeholder="John Doe" 
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
          <input 
            v-model="email" 
            type="email" 
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
            placeholder="your@email.com" 
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
          <input 
            v-model="password" 
            type="password" 
            required
            minlength="6"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
            placeholder="At least 6 characters" 
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Role</label>
          <select 
            v-model="role" 
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Select a role</option>
            <option value="student">Student</option>
            <option value="teacher">Teacher</option>
          </select>
        </div>

        <div v-if="role === 'student'">
          <label class="block text-sm font-medium text-gray-700 mb-2">Student ID</label>
          <input 
            v-model="studentId" 
            type="text"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
            placeholder="Optional" 
          />
        </div>

        <div v-if="role === 'teacher'">
          <label class="block text-sm font-medium text-gray-700 mb-2">Employee ID</label>
          <input 
            v-model="employeeId" 
            type="text"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
            placeholder="Optional" 
          />
        </div>

        <button 
          type="submit" 
          :disabled="loading"
          class="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50 mt-6"
        >
          {{ loading ? 'Creating Account...' : 'Create Account' }}
        </button>
      </form>

      <p class="text-center mt-6 text-gray-600">
        Already have an account? 
        <router-link to="/login" class="text-blue-600 hover:text-blue-700 font-semibold">Login</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const fullName = ref('')
const email = ref('')
const password = ref('')
const role = ref('')
const studentId = ref('')
const employeeId = ref('')
const loading = ref(false)
const error = ref('')

const router = useRouter()
const authStore = useAuthStore()

const handleRegister = async () => {
  error.value = ''
  loading.value = true
  
  try {
    const userData = {
      email: email.value,
      password: password.value,
      full_name: fullName.value,
      role: role.value
    }

    if (role.value === 'student' && studentId.value) {
      userData.student_id = studentId.value
    }
    if (role.value === 'teacher' && employeeId.value) {
      userData.employee_id = employeeId.value
    }

    await authStore.register(userData)
    router.push('/login')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Registration failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
