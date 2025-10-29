<template>
  <div class="min-h-screen bg-light">
    <!-- Header -->
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-8 py-6 flex justify-between items-center">
        <h1 class="text-3xl font-bold text-primary">Student Dashboard</h1>
        <div class="flex items-center gap-4">
          <router-link to="/getting-started" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium">
            📖 Getting Started
          </router-link>
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
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <router-link 
          to="/join-test" 
          class="bg-gradient-to-br from-indigo-500 to-purple-600 text-white rounded-xl p-8 hover:shadow-xl transition-all"
        >
          <div class="text-5xl mb-4">🎯</div>
          <h3 class="text-2xl font-bold mb-2">Join Test</h3>
          <p class="text-indigo-100">Enter 4-digit code to join proctored test</p>
        </router-link>
        
        <router-link 
          to="/student/learning" 
          class="bg-gradient-to-br from-blue-500 to-cyan-600 text-white rounded-xl p-8 hover:shadow-xl transition-all"
        >
          <div class="text-5xl mb-4">📖</div>
          <h3 class="text-2xl font-bold mb-2">AI Learning</h3>
          <p class="text-blue-100">Upload PDFs and learn with AI assistance</p>
        </router-link>
        
        <router-link 
          to="/course-generator" 
          class="bg-gradient-to-br from-green-500 to-teal-600 text-white rounded-xl p-8 hover:shadow-xl transition-all"
        >
          <div class="text-5xl mb-4">📚</div>
          <h3 class="text-2xl font-bold mb-2">AI Courses</h3>
          <p class="text-green-100">Continue learning or generate new course</p>
        </router-link>
      </div>

      <!-- My AI Courses Section -->
      <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h2 class="text-2xl font-bold text-gray-900">📚 My AI Courses</h2>
            <p class="text-gray-600 mt-1">Continue your personalized learning journey</p>
          </div>
          <button 
            @click="router.push('/course-generator')" 
            class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition font-semibold"
          >
            + Generate New Course
          </button>
        </div>

        <!-- Loading State -->
        <div v-if="loadingCourses" class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          <p class="text-gray-600 mt-4">Loading your courses...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="myCourses.length === 0" class="text-center py-12">
          <div class="text-6xl mb-4">📚</div>
          <h3 class="text-xl font-semibold text-gray-900 mb-2">No Courses Yet</h3>
          <p class="text-gray-600 mb-6">Start your learning journey by generating your first AI-powered course</p>
          <button 
            @click="router.push('/course-generator')" 
            class="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition font-semibold"
          >
            🚀 Generate Your First Course
          </button>
        </div>

        <!-- Courses Grid -->
        <div v-else class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div 
            v-for="course in myCourses" 
            :key="course.id"
            @click="viewCourse(course)"
            class="bg-gradient-to-br from-white to-indigo-50 border border-indigo-100 rounded-xl p-6 hover:shadow-xl transition-all duration-300 cursor-pointer group"
          >
            <div class="flex items-start justify-between mb-3">
              <div class="text-3xl">🎓</div>
              <span 
                class="px-3 py-1 text-xs font-semibold rounded-full"
                :class="{
                  'bg-green-100 text-green-700': course.difficulty === 'beginner',
                  'bg-yellow-100 text-yellow-700': course.difficulty === 'medium',
                  'bg-red-100 text-red-700': course.difficulty === 'advanced'
                }"
              >
                {{ course.difficulty }}
              </span>
            </div>
            
            <h3 class="text-lg font-bold text-gray-900 mb-2 line-clamp-2 group-hover:text-indigo-600 transition">
              {{ course.course_title || course.topic }}
            </h3>
            
            <p class="text-gray-600 text-sm mb-4 line-clamp-2">
              {{ course.description || `Learn ${course.topic}` }}
            </p>
            
            <div class="flex items-center gap-4 text-sm text-gray-500 mb-3">
              <span>📅 {{ course.total_days }} days</span>
              <span>📖 {{ course.daily_lessons_count }} lessons</span>
            </div>
            
            <div class="flex items-center justify-between">
              <span class="text-xs text-gray-400">{{ formatDate(course.created_at) }}</span>
              <button class="text-indigo-600 hover:text-indigo-700 font-semibold text-sm group-hover:translate-x-1 transition">
                View Course →
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Topic Selection (Legacy) -->
      <section v-if="false" class="mb-12">
        <h2 class="text-2xl font-bold mb-6">Select a Topic to Learn</h2>
        <div class="flex gap-4">
          <input v-model="selectedTopic" type="text" class="input-field flex-1" placeholder="Enter topic (e.g., Calculus, Physics)" />
          <button @click="generateRoadmap" class="btn-primary">
            Generate Roadmap
          </button>
        </div>
      </section>

      <!-- Learning Roadmap -->
      <section v-if="roadmap" class="mb-12">
        <h2 class="text-2xl font-bold mb-6">Your Learning Roadmap: {{ selectedTopic }}</h2>
        <div class="space-y-4">
          <div v-for="(step, index) in roadmap" :key="index" class="card flex items-start gap-4">
            <div class="flex-shrink-0 w-10 h-10 bg-primary text-white rounded-full flex items-center justify-center font-bold">
              {{ index + 1 }}
            </div>
            <div class="flex-1">
              <h3 class="text-lg font-semibold">{{ step.title }}</h3>
              <p class="text-gray-600">{{ step.description }}</p>
              <p class="text-sm text-gray-500 mt-2">Duration: {{ step.duration }}</p>
            </div>
            <span class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold">{{ step.status }}</span>
          </div>
        </div>
      </section>

      <!-- Available Tests -->
      <section>
        <h2 class="text-2xl font-bold mb-6">Available Tests</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="test in availableTests" :key="test.id" class="card">
            <h3 class="text-xl font-bold mb-2">{{ test.title }}</h3>
            <p class="text-gray-600 mb-4">{{ test.description }}</p>
            <div class="flex justify-between items-center mb-4">
              <span class="text-sm text-gray-500">Duration: {{ test.duration }} min</span>
              <span class="text-sm font-semibold text-primary">{{ test.questions }} questions</span>
            </div>
            <router-link :to="`/student/test/${test.id}`" class="btn-primary w-full text-center">
              Start Test
            </router-link>
          </div>
        </div>
      </section>

      <!-- Analytics -->
      <section class="mt-12">
        <h2 class="text-2xl font-bold mb-6">Your Performance</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="card text-center">
            <p class="text-gray-600 mb-2">Tests Completed</p>
            <p class="text-4xl font-bold text-primary">{{ analytics.testsCompleted }}</p>
          </div>
          <div class="card text-center">
            <p class="text-gray-600 mb-2">Average Score</p>
            <p class="text-4xl font-bold text-secondary">{{ analytics.averageScore }}%</p>
          </div>
          <div class="card text-center">
            <p class="text-gray-600 mb-2">Learning Hours</p>
            <p class="text-4xl font-bold text-accent">{{ analytics.learningHours }}</p>
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
import { useToast } from 'vue-toastification'

const authStore = useAuthStore()
const router = useRouter()
const toast = useToast()

const selectedTopic = ref('')
const roadmap = ref(null)
const myCourses = ref([])
const loadingCourses = ref(false)

// Mock data
const availableTests = ref([
  { id: 1, title: 'Calculus Basics', description: 'Test your knowledge of calculus fundamentals', duration: 60, questions: 20 },
  { id: 2, title: 'Linear Algebra', description: 'Matrices, vectors, and transformations', duration: 45, questions: 15 },
  { id: 3, title: 'Differential Equations', description: 'Solving differential equations', duration: 90, questions: 25 }
])

const analytics = ref({
  testsCompleted: 5,
  averageScore: 82,
  learningHours: 24
})

// Fetch user's courses
const fetchCourses = async () => {
  loadingCourses.value = true
  try {
    const response = await api.get('/ai/my-courses')
    myCourses.value = response.data.courses
  } catch (error) {
    console.error('Failed to fetch courses:', error)
    toast.error('Failed to load your courses')
  } finally {
    loadingCourses.value = false
  }
}

// View course details
const viewCourse = async (course) => {
  try {
    const response = await api.get(`/ai/course/${course.id}`)
    const courseData = response.data.course
    
    // Store course data in sessionStorage and navigate to course generator
    sessionStorage.setItem('viewCourse', JSON.stringify({
      course: courseData,
      metadata: response.data.metadata
    }))
    
    router.push('/course-generator')
  } catch (error) {
    console.error('Failed to load course:', error)
    toast.error('Failed to load course details')
  }
}

// Format date
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`
  return date.toLocaleDateString()
}

const generateRoadmap = () => {
  // TODO: Call API to generate AI roadmap
  roadmap.value = [
    { title: 'Fundamentals', description: 'Learn the basics of ' + selectedTopic.value, duration: '2 hours', status: 'In Progress' },
    { title: 'Core Concepts', description: 'Deep dive into core concepts', duration: '4 hours', status: 'Pending' },
    { title: 'Advanced Topics', description: 'Explore advanced applications', duration: '3 hours', status: 'Pending' },
    { title: 'Practice Problems', description: 'Solve real-world problems', duration: '2 hours', status: 'Pending' }
  ]
}

const logout = () => {
  authStore.logout()
  router.push('/')
}

// Load courses on mount
onMounted(() => {
  fetchCourses()
})
</script>
