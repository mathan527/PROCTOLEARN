<template>
  <div class="min-h-screen bg-light">
    <!-- Header -->
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-8 py-6 flex justify-between items-center">
        <h1 class="text-3xl font-bold text-primary">Teacher Dashboard</h1>
        <div class="flex items-center gap-4">
          <router-link to="/course-generator" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition font-medium">
            🎓 AI Courses
          </router-link>
          <span class="text-gray-600">Welcome, {{ authStore.user?.name }}</span>
          <button @click="logout" class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600">
            Logout
          </button>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-8 py-12">
      <!-- Quick Actions -->
      <section class="mb-12">
        <h2 class="text-2xl font-bold mb-6">Quick Actions</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <router-link 
            to="/teacher/test-creation" 
            class="bg-gradient-to-br from-indigo-500 to-purple-600 text-white rounded-xl p-8 hover:shadow-xl transition-all"
          >
            <div class="text-5xl mb-4">📝</div>
            <h3 class="text-2xl font-bold mb-2">Create Proctored Test</h3>
            <p class="text-indigo-100">Generate 4-digit code, add questions, enable monitoring</p>
          </router-link>
          
          <router-link 
            to="/course-generator" 
            class="bg-gradient-to-br from-green-500 to-teal-600 text-white rounded-xl p-8 hover:shadow-xl transition-all"
          >
            <div class="text-5xl mb-4">🎓</div>
            <h3 class="text-2xl font-bold mb-2">AI Course Generator</h3>
            <p class="text-green-100">Create comprehensive courses with AI</p>
          </router-link>
          
          <router-link 
            to="/teacher/create-test" 
            class="bg-gradient-to-br from-blue-500 to-cyan-600 text-white rounded-xl p-8 hover:shadow-xl transition-all"
          >
            <div class="text-5xl mb-4">⚡</div>
            <h3 class="text-2xl font-bold mb-2">Quick Test</h3>
            <p class="text-blue-100">Create simple test without proctoring</p>
          </router-link>
        </div>
      </section>

      <!-- Active Sessions -->
      <section class="mb-12">
        <h2 class="text-2xl font-bold mb-6">Active Test Sessions</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div v-for="session in activeSessions" :key="session.id" class="card">
            <div class="flex justify-between items-start mb-4">
              <h3 class="text-xl font-bold">{{ session.testName }}</h3>
              <span :class="session.status === 'live' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'" class="px-3 py-1 rounded-full text-sm font-semibold">
                {{ session.status }}
              </span>
            </div>
            <p class="text-gray-600 mb-4">{{ session.studentsCount }} students</p>
            <router-link :to="`/teacher/monitor/${session.id}`" class="btn-secondary w-full text-center">
              Monitor Session
            </router-link>
          </div>
        </div>
      </section>

      <!-- Created Tests -->
      <section>
        <h2 class="text-2xl font-bold mb-6">Your Tests</h2>
        <div class="space-y-4">
          <div v-for="test in tests" :key="test.id" class="card">
            <div class="flex justify-between items-start mb-4">
              <div>
                <h3 class="text-lg font-bold">{{ test.title }}</h3>
                <p class="text-gray-600">{{ test.questions?.length || 0 }} questions • {{ test.duration_minutes }} minutes</p>
                <p class="text-sm text-gray-500 mt-2">Code: <span class="font-mono font-bold text-blue-600">{{ test.test_code }}</span></p>
                <p class="text-sm text-gray-500">Created: {{ new Date(test.created_at).toLocaleDateString() }}</p>
              </div>
              <div class="flex flex-col gap-2">
                <span class="px-3 py-1 rounded-full text-xs font-semibold"
                  :class="test.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'">
                  {{ test.is_active ? '🟢 Active' : '⚫ Inactive' }}
                </span>
              </div>
            </div>
            
            <!-- Stats -->
            <div class="grid grid-cols-3 gap-4 mb-4 p-3 bg-gray-50 rounded-lg">
              <div class="text-center">
                <p class="text-2xl font-bold text-blue-600">{{ test.attemptCount || 0 }}</p>
                <p class="text-xs text-gray-600">Attempts</p>
              </div>
              <div class="text-center">
                <p class="text-2xl font-bold text-green-600">{{ test.completedCount || 0 }}</p>
                <p class="text-xs text-gray-600">Completed</p>
              </div>
              <div class="text-center">
                <p class="text-2xl font-bold text-orange-600">{{ test.avgScore || 0 }}%</p>
                <p class="text-xs text-gray-600">Avg Score</p>
              </div>
            </div>

            <div class="flex gap-2">
              <button @click="viewResults(test.id)" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center gap-2">
                <span>📊</span> View Results
              </button>
              <button @click="exportAnswers(test.id)" class="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 flex items-center gap-2">
                <span>📥</span> Export Answers
              </button>
              <router-link :to="`/teacher/proctoring/${test.id}`" class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2 animate-pulse">
                <span>�️</span> Monitor Live
              </router-link>
            </div>
          </div>
          
          <div v-if="tests.length === 0" class="card text-center py-12">
            <div class="text-6xl mb-4">📝</div>
            <p class="text-gray-600 mb-4">No tests created yet</p>
            <router-link to="/teacher/test-creation" class="btn-primary inline-block">
              Create Your First Test
            </router-link>
          </div>
        </div>
      </section>

      <!-- Test Results Modal -->
      <div v-if="showResultsModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" @click="showResultsModal = false">
        <div class="bg-white rounded-xl max-w-6xl w-full max-h-[90vh] overflow-y-auto" @click.stop>
          <div class="sticky top-0 bg-white border-b p-6 flex justify-between items-center">
            <h2 class="text-2xl font-bold">Test Results: {{ selectedTest?.title }}</h2>
            <button @click="showResultsModal = false" class="text-gray-500 hover:text-gray-700 text-2xl">×</button>
          </div>
          
          <div class="p-6">
            <div class="overflow-x-auto">
              <table class="w-full">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-3 text-left text-sm font-semibold">Student</th>
                    <th class="px-4 py-3 text-left text-sm font-semibold">Status</th>
                    <th class="px-4 py-3 text-left text-sm font-semibold">Score</th>
                    <th class="px-4 py-3 text-left text-sm font-semibold">Time Taken</th>
                    <th class="px-4 py-3 text-left text-sm font-semibold">Violations</th>
                    <th class="px-4 py-3 text-left text-sm font-semibold">Started At</th>
                  </tr>
                </thead>
                <tbody class="divide-y">
                  <tr v-for="attempt in testResults" :key="attempt.id" class="hover:bg-gray-50">
                    <td class="px-4 py-3">{{ attempt.student_name }}</td>
                    <td class="px-4 py-3">
                      <span class="px-2 py-1 rounded-full text-xs font-semibold"
                        :class="attempt.status === 'completed' ? 'bg-green-100 text-green-800' : 
                                attempt.status === 'in_progress' ? 'bg-blue-100 text-blue-800' : 
                                'bg-gray-100 text-gray-800'">
                        {{ attempt.status }}
                      </span>
                    </td>
                    <td class="px-4 py-3 font-bold" :class="attempt.score >= 70 ? 'text-green-600' : 'text-red-600'">
                      {{ attempt.score !== null ? attempt.score.toFixed(1) + '%' : 'N/A' }}
                    </td>
                    <td class="px-4 py-3">{{ formatDuration(attempt.time_taken) }}</td>
                    <td class="px-4 py-3">
                      <span class="px-2 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-800">
                        {{ attempt.proctoring_violations?.length || 0 }}
                      </span>
                    </td>
                    <td class="px-4 py-3 text-sm text-gray-600">
                      {{ new Date(attempt.started_at).toLocaleString() }}
                    </td>
                  </tr>
                </tbody>
              </table>
              
              <div v-if="testResults.length === 0" class="text-center py-12 text-gray-500">
                No attempts yet for this test
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Analytics -->
      <section class="mt-12">
        <h2 class="text-2xl font-bold mb-6">Class Analytics</h2>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div class="card text-center">
            <p class="text-gray-600 mb-2">Total Students</p>
            <p class="text-4xl font-bold text-primary">{{ analytics.totalStudents }}</p>
          </div>
          <div class="card text-center">
            <p class="text-gray-600 mb-2">Tests Created</p>
            <p class="text-4xl font-bold text-secondary">{{ analytics.testsCreated }}</p>
          </div>
          <div class="card text-center">
            <p class="text-gray-600 mb-2">Avg. Score</p>
            <p class="text-4xl font-bold text-accent">{{ analytics.avgScore }}%</p>
          </div>
          <div class="card text-center">
            <p class="text-gray-600 mb-2">Violations</p>
            <p class="text-4xl font-bold text-red-500">{{ analytics.violations }}</p>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const authStore = useAuthStore()
const router = useRouter()

const tests = ref([])
const testResults = ref([])
const showResultsModal = ref(false)
const selectedTest = ref(null)

const activeSessions = ref([
  { id: 1, testName: 'Calculus Midterm', status: 'live', studentsCount: 12 },
  { id: 2, testName: 'Physics Quiz', status: 'ended', studentsCount: 8 }
])

const analytics = ref({
  totalStudents: 45,
  testsCreated: 8,
  avgScore: 78,
  violations: 3
})

const loadTests = async () => {
  try {
    const response = await api.get('/tests')
    tests.value = response.data
    
    // Load attempt counts for each test
    for (const test of tests.value) {
      try {
        const attemptsResponse = await api.get(`/tests/${test.id}/attempts`)
        test.attemptCount = attemptsResponse.data.length
        test.completedCount = attemptsResponse.data.filter(a => a.status === 'completed').length
        
        // Calculate average score
        const completedAttempts = attemptsResponse.data.filter(a => a.status === 'completed' && a.score !== null)
        if (completedAttempts.length > 0) {
          const totalScore = completedAttempts.reduce((sum, a) => sum + a.score, 0)
          test.avgScore = Math.round(totalScore / completedAttempts.length)
        }
      } catch (error) {
        console.error(`Failed to load attempts for test ${test.id}:`, error)
      }
    }
  } catch (error) {
    console.error('Failed to load tests:', error)
  }
}

const viewResults = async (testId) => {
  try {
    selectedTest.value = tests.value.find(t => t.id === testId)
    const response = await api.get(`/tests/${testId}/attempts`)
    testResults.value = response.data
    showResultsModal.value = true
  } catch (error) {
    console.error('Failed to load test results:', error)
    alert('Failed to load test results')
  }
}

const exportAnswers = async (testId) => {
  try {
    const test = tests.value.find(t => t.id === testId)
    const response = await api.get(`/tests/${testId}/attempts`)
    const attempts = response.data
    
    if (attempts.length === 0) {
      alert('No attempts to export')
      return
    }
    
    // Get all answers for this test
    const allAnswers = []
    for (const attempt of attempts) {
      try {
        const answersResponse = await api.get(`/questions/answers/${attempt.id}`)
        const answers = answersResponse.data
        
        answers.forEach(answer => {
          allAnswers.push({
            'Student Name': attempt.student_name,
            'Student ID': attempt.user_id,
            'Question': answer.question_text,
            'Student Answer': answer.answer_text || 'No answer',
            'Correct Answer': answer.correct_answer || 'N/A',
            'Is Correct': answer.is_correct ? 'Yes' : 'No',
            'Score': attempt.score ? attempt.score.toFixed(1) + '%' : 'N/A',
            'Status': attempt.status,
            'Violations': attempt.proctoring_violations?.length || 0,
            'Started At': new Date(attempt.started_at).toLocaleString(),
            'Completed At': attempt.completed_at ? new Date(attempt.completed_at).toLocaleString() : 'N/A'
          })
        })
      } catch (error) {
        console.error(`Failed to load answers for attempt ${attempt.id}:`, error)
      }
    }
    
    // Convert to CSV
    if (allAnswers.length === 0) {
      alert('No answers to export')
      return
    }
    
    const headers = Object.keys(allAnswers[0])
    const csvContent = [
      headers.join(','),
      ...allAnswers.map(row => 
        headers.map(header => {
          const value = row[header]?.toString() || ''
          // Escape quotes and wrap in quotes if contains comma
          return value.includes(',') || value.includes('"') 
            ? `"${value.replace(/"/g, '""')}"` 
            : value
        }).join(',')
      )
    ].join('\n')
    
    // Download CSV
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${test.title.replace(/\s+/g, '_')}_answers_${new Date().toISOString().split('T')[0]}.csv`
    link.click()
    
    alert('Answers exported successfully!')
  } catch (error) {
    console.error('Failed to export answers:', error)
    alert('Failed to export answers')
  }
}

const formatDuration = (seconds) => {
  if (!seconds) return 'N/A'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}m ${secs}s`
}

const logout = () => {
  authStore.logout()
  router.push('/')
}

onMounted(() => {
  loadTests()
})
</script>
