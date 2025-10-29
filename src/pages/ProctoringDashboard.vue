<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100">
    <header class="bg-white shadow-md sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-6 py-4">
        <div class="flex justify-between items-center">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">🛡️ Live Proctoring Monitor</h1>
            <p class="text-sm text-gray-600">Real-time student monitoring for: {{ test?.title }}</p>
          </div>
          <button @click="router.back()" class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">
            ← Back
          </button>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-6 py-8">
      <!-- Stats Overview -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div class="bg-white rounded-xl shadow p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600">Total Students</p>
              <p class="text-3xl font-bold text-blue-600">{{ activeStudents.length }}</p>
            </div>
            <div class="p-3 bg-blue-100 rounded-full">
              <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600">Active Violations</p>
              <p class="text-3xl font-bold text-red-600">{{ totalViolations }}</p>
            </div>
            <div class="p-3 bg-red-100 rounded-full">
              <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600">Flagged Students</p>
              <p class="text-3xl font-bold text-yellow-600">{{ flaggedStudents }}</p>
            </div>
            <div class="p-3 bg-yellow-100 rounded-full">
              <svg class="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600">AI Detection</p>
              <p class="text-3xl font-bold text-green-600">Active</p>
            </div>
            <div class="p-3 bg-green-100 rounded-full animate-pulse">
              <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Student Grid -->
      <div class="bg-white rounded-xl shadow-lg p-6">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-xl font-bold text-gray-900">Live Student Feeds</h2>
          <div class="flex gap-2">
            <button @click="viewMode = 'grid'" :class="viewMode === 'grid' ? 'bg-purple-600 text-white' : 'bg-gray-200 text-gray-700'" class="px-4 py-2 rounded-lg">
              Grid View
            </button>
            <button @click="viewMode = 'list'" :class="viewMode === 'list' ? 'bg-purple-600 text-white' : 'bg-gray-200 text-gray-700'" class="px-4 py-2 rounded-lg">
              List View
            </button>
          </div>
        </div>

        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="student in activeStudents" :key="student.id" 
               :class="['rounded-xl border-4 overflow-hidden shadow-lg relative', getStudentBorderColor(student)]">
            
            <!-- Waiting Room Banner -->
            <div v-if="student.inWaitingRoom" class="absolute top-0 left-0 right-0 bg-red-600 text-white text-center py-1 text-xs font-bold z-10 animate-pulse">
              🚨 IN WAITING ROOM 🚨
            </div>
            
            <!-- Camera Feed -->
            <div class="relative bg-black aspect-video" :class="student.inWaitingRoom ? 'mt-6' : ''">
              <video :ref="el => studentVideoRefs[student.id] = el" 
                     autoplay muted playsinline 
                     class="w-full h-full object-cover">
              </video>
              
              <!-- Status Overlay -->
              <div class="absolute top-2 left-2 right-2 flex justify-between">
                <div :class="['px-3 py-1 rounded-full text-xs font-bold', getStatusBadgeColor(student)]">
                  {{ getStatusText(student) }}
                </div>
                <div class="px-3 py-1 rounded-full text-xs font-bold bg-red-600 text-white">
                  Violations: {{ student.violationCount || 0 }}
                </div>
              </div>

              <!-- Face Detection Box -->
              <canvas v-if="student.faceBox" 
                      class="absolute inset-0 pointer-events-none"
                      :width="640" :height="480"></canvas>
            </div>

            <!-- Student Info -->
            <div class="p-4 bg-white">
              <div class="flex items-center justify-between mb-2">
                <h3 class="font-bold text-gray-900">{{ student.name }}</h3>
                <span class="text-xs text-gray-500">ID: {{ student.studentId }}</span>
              </div>
              
              <!-- Detection Status Icons -->
              <div class="flex gap-2 text-xs">
                <span :class="student.faceDetected ? 'text-green-600' : 'text-red-600'" class="flex items-center gap-1">
                  <span class="w-2 h-2 rounded-full" :class="student.faceDetected ? 'bg-green-600' : 'bg-red-600'"></span>
                  Face
                </span>
                <span :class="student.eyesOpen ? 'text-green-600' : 'text-yellow-600'" class="flex items-center gap-1">
                  <span class="w-2 h-2 rounded-full" :class="student.eyesOpen ? 'bg-green-600' : 'bg-yellow-600'"></span>
                  Eyes
                </span>
                <span :class="student.lookingAtScreen ? 'text-green-600' : 'text-yellow-600'" class="flex items-center gap-1">
                  <span class="w-2 h-2 rounded-full" :class="student.lookingAtScreen ? 'bg-green-600' : 'bg-yellow-600'"></span>
                  Focus
                </span>
                <span :class="student.fullscreen ? 'text-green-600' : 'text-red-600'" class="flex items-center gap-1">
                  <span class="w-2 h-2 rounded-full" :class="student.fullscreen ? 'bg-green-600' : 'bg-red-600'"></span>
                  Fullscreen
                </span>
              </div>

              <!-- Recent Violations -->
              <div v-if="student.recentViolations?.length > 0" class="mt-3 pt-3 border-t border-gray-200">
                <p class="text-xs font-semibold text-red-600 mb-1">Recent Violations:</p>
                <div class="space-y-1">
                  <p v-for="(violation, idx) in student.recentViolations.slice(0, 2)" :key="idx" class="text-xs text-gray-600">
                    • {{ violation.type.replace(/_/g, ' ') }} - {{ formatTime(violation.timestamp) }}
                  </p>
                </div>
              </div>
              
              <!-- Teacher Controls -->
              <div v-if="student.inWaitingRoom" class="mt-3 pt-3 border-t border-gray-200">
                <p class="text-xs font-semibold text-purple-600 mb-2">🛡️ Teacher Controls:</p>
                <div class="grid grid-cols-3 gap-1">
                  <button @click="teacherAction(student.id, 'admit')" class="px-2 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700">
                    ✓ Admit
                  </button>
                  <button @click="teacherAction(student.id, 'pause')" class="px-2 py-1 bg-yellow-600 text-white text-xs rounded hover:bg-yellow-700">
                    ⏸ Pause
                  </button>
                  <button @click="teacherAction(student.id, 'terminate')" class="px-2 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700">
                    ✗ End
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- List View -->
        <div v-else class="space-y-4">
          <div v-for="student in activeStudents" :key="student.id" 
               :class="['flex gap-4 p-4 rounded-xl border-2', getStudentBorderColor(student)]">
            <div class="relative w-48 h-36 bg-black rounded-lg overflow-hidden flex-shrink-0">
              <video :ref="el => studentVideoRefs[student.id] = el" 
                     autoplay muted playsinline 
                     class="w-full h-full object-cover">
              </video>
            </div>
            
            <div class="flex-1">
              <div class="flex justify-between items-start mb-2">
                <div>
                  <h3 class="font-bold text-gray-900">{{ student.name }}</h3>
                  <p class="text-sm text-gray-600">{{ student.studentId }}</p>
                </div>
                <div :class="['px-3 py-1 rounded-full text-xs font-bold', getStatusBadgeColor(student)]">
                  {{ getStatusText(student) }}
                </div>
              </div>

              <div class="grid grid-cols-4 gap-2 mb-3">
                <div class="text-center p-2 bg-gray-50 rounded">
                  <p class="text-xs text-gray-600">Face</p>
                  <p :class="student.faceDetected ? 'text-green-600' : 'text-red-600'" class="text-lg font-bold">
                    {{ student.faceDetected ? '✓' : '✗' }}
                  </p>
                </div>
                <div class="text-center p-2 bg-gray-50 rounded">
                  <p class="text-xs text-gray-600">Eyes</p>
                  <p :class="student.eyesOpen ? 'text-green-600' : 'text-yellow-600'" class="text-lg font-bold">
                    {{ student.eyesOpen ? '✓' : '✗' }}
                  </p>
                </div>
                <div class="text-center p-2 bg-gray-50 rounded">
                  <p class="text-xs text-gray-600">Focus</p>
                  <p :class="student.lookingAtScreen ? 'text-green-600' : 'text-yellow-600'" class="text-lg font-bold">
                    {{ student.lookingAtScreen ? '✓' : '✗' }}
                  </p>
                </div>
                <div class="text-center p-2 bg-gray-50 rounded">
                  <p class="text-xs text-gray-600">Violations</p>
                  <p class="text-red-600 text-lg font-bold">{{ student.violationCount || 0 }}</p>
                </div>
              </div>

              <div v-if="student.recentViolations?.length > 0" class="space-y-1">
                <p v-for="(violation, idx) in student.recentViolations.slice(0, 3)" :key="idx" class="text-xs text-gray-600">
                  🚨 {{ violation.type.replace(/_/g, ' ') }} - {{ formatTime(violation.timestamp) }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- No Students -->
        <div v-if="activeStudents.length === 0" class="text-center py-12">
          <div class="text-6xl mb-4">👥</div>
          <h3 class="text-xl font-bold text-gray-900 mb-2">No Active Students</h3>
          <p class="text-gray-600">Students will appear here when they start the test</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'

const route = useRoute()
const router = useRouter()

const test = ref(null)
const activeStudents = ref([])
const studentVideoRefs = ref({})
const viewMode = ref('grid')
const socket = ref(null)

const totalViolations = computed(() => 
  activeStudents.value.reduce((sum, s) => sum + (s.violationCount || 0), 0)
)

const flaggedStudents = computed(() => 
  activeStudents.value.filter(s => (s.violationCount || 0) >= 5).length
)

const getStudentBorderColor = (student) => {
  const count = student.violationCount || 0
  if (count >= 10) return 'border-red-600'
  if (count >= 5) return 'border-yellow-500'
  return 'border-green-500'
}

const getStatusBadgeColor = (student) => {
  const count = student.violationCount || 0
  if (count >= 10) return 'bg-red-600 text-white'
  if (count >= 5) return 'bg-yellow-500 text-white'
  return 'bg-green-500 text-white'
}

const getStatusText = (student) => {
  const count = student.violationCount || 0
  if (count >= 10) return '🚨 HIGH RISK'
  if (count >= 5) return '⚠️ FLAGGED'
  return '✓ NORMAL'
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString()
}

const teacherAction = async (studentId, action) => {
  try {
    const actionLabels = {
      admit: 'admit student back into test',
      pause: 'pause student\'s test',
      terminate: 'terminate student\'s test'
    }
    
    if (action === 'terminate') {
      if (!confirm(`Are you sure you want to TERMINATE this student's test? This cannot be undone.`)) {
        return
      }
    }
    
    console.log(`🎓 Teacher action: ${action} for student ${studentId}`)
    
    const response = await api.post(`/proctoring/teacher-action/${route.params.testId}`, {
      student_id: studentId,
      action: action
    })
    
    console.log('✅ Action successful:', response.data)
    
    // Update student status in UI
    const student = activeStudents.value.find(s => s.id === studentId)
    if (student) {
      if (action === 'admit') {
        student.inWaitingRoom = false
        alert(`Student admitted back to test!`)
      } else if (action === 'pause') {
        student.paused = true
        alert(`Student's test has been paused`)
      } else if (action === 'terminate') {
        // Remove from list
        activeStudents.value = activeStudents.value.filter(s => s.id !== studentId)
        alert(`Student's test has been terminated`)
      }
    }
    
    // Notify via WebSocket
    if (socket.value) {
      socket.value.emit('teacher_action', {
        studentId: studentId,
        action: action,
        testId: route.params.testId
      })
    }
  } catch (error) {
    console.error('Failed to perform teacher action:', error)
    alert('Failed to perform action: ' + (error.response?.data?.detail || error.message))
  }
}

const connectWebSocket = () => {
  const wsUrl = `ws://localhost:8000/ws/proctoring/${route.params.testId}/teacher`
  socket.value = new WebSocket(wsUrl)

  socket.value.onopen = () => {
    console.log('✅ Connected to proctoring WebSocket')
  }

  socket.value.onmessage = async (event) => {
    const data = JSON.parse(event.data)
    
    if (data.type === 'student_joined') {
      activeStudents.value.push({
        id: data.studentId,
        name: data.studentName,
        studentId: data.studentNumber,
        faceDetected: true,
        eyesOpen: true,
        lookingAtScreen: true,
        fullscreen: false,
        violationCount: 0,
        recentViolations: [],
        inWaitingRoom: false,
        paused: false
      })
    } else if (data.type === 'camera_frame') {
      // Update video feed
      const video = studentVideoRefs.value[data.studentId]
      if (video && data.frame) {
        // Convert base64 to blob and set as video source
        // In production, use WebRTC for better performance
      }
    } else if (data.type === 'proctoring_status') {
      const student = activeStudents.value.find(s => s.id === data.studentId)
      if (student) {
        student.faceDetected = data.faceDetected
        student.eyesOpen = data.eyesOpen
        student.lookingAtScreen = data.lookingAtScreen
        student.fullscreen = data.fullscreen
      }
    } else if (data.type === 'violation') {
      const student = activeStudents.value.find(s => s.id === data.studentId)
      if (student) {
        student.violationCount = (student.violationCount || 0) + 1
        student.recentViolations = student.recentViolations || []
        student.recentViolations.unshift({
          type: data.violationType,
          timestamp: new Date().toISOString()
        })
        if (student.recentViolations.length > 10) {
          student.recentViolations = student.recentViolations.slice(0, 10)
        }
      }
    } else if (data.type === 'student_flagged' || data.type === 'severe_violations') {
      // Student sent to waiting room
      const student = activeStudents.value.find(s => s.id === data.studentId)
      if (student) {
        student.inWaitingRoom = true
        student.violationCount = (student.violationCount || 0) + (data.score || 10)
        
        // Show alert to teacher
        alert(`🚨 ALERT: ${student.name} has been flagged for excessive violations!\n\nScore: ${data.score || 10}\nReason: ${data.details || 'Multiple violations detected'}\n\nStudent is now in the waiting room.`)
      }
    }
  }

  socket.value.onclose = () => {
    console.log('❌ Disconnected from proctoring WebSocket')
    // Reconnect after 3 seconds
    setTimeout(connectWebSocket, 3000)
  }
}

onMounted(async () => {
  try {
    const response = await api.get(`/tests/${route.params.testId}`)
    test.value = response.data
    connectWebSocket()
  } catch (error) {
    console.error('Failed to load test:', error)
  }
})

onUnmounted(() => {
  if (socket.value) {
    socket.value.close()
  }
})
</script>
