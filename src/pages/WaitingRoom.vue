<template>
  <div class="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 flex items-center justify-center p-6">
    <div class="bg-white rounded-2xl shadow-2xl p-8 max-w-2xl w-full text-center">
      <div class="text-8xl mb-6">{{ isInitialEntry ? '⏳' : '⏸️' }}</div>
      <h1 class="text-3xl font-bold mb-4" :class="isInitialEntry ? 'text-blue-600' : 'text-red-600'">
        {{ isInitialEntry ? 'Waiting for Teacher Approval' : 'Test Paused - Awaiting Review' }}
      </h1>
      
      <div v-if="!isInitialEntry" class="bg-red-50 border-2 border-red-200 rounded-xl p-6 mb-6">
        <h2 class="font-bold text-lg text-gray-900 mb-3">🚨 Suspicious Activity Detected</h2>
        <div class="text-left space-y-2 text-sm">
          <p v-for="(violation, idx) in suspiciousReasons" :key="idx" class="text-gray-700">
            • {{ violation }}
          </p>
        </div>
      </div>

      <div v-else class="bg-blue-50 border-2 border-blue-200 rounded-xl p-6 mb-6">
        <h2 class="font-bold text-lg text-gray-900 mb-3">👋 Welcome to the Test</h2>
        <p class="text-gray-700">
          This test requires manual approval. Your teacher will admit you shortly after verifying your setup.
        </p>
      </div>

      <div class="space-y-4 mb-6">
        <div class="flex items-center justify-center gap-3 text-gray-600">
          <div class="w-3 h-3 rounded-full animate-pulse" :class="isInitialEntry ? 'bg-blue-500' : 'bg-yellow-500'"></div>
          <p>{{ isInitialEntry ? 'Waiting for teacher to start your test' : `Your test has been paused by ${pausedBy}` }}</p>
        </div>
        <p class="text-gray-600">Please wait while your teacher reviews {{ isInitialEntry ? 'your setup' : 'your activity' }}.</p>
        <p class="text-sm text-gray-500">Do not close this window or refresh the page.</p>
      </div>

      <!-- Live Timer -->
      <div class="bg-gray-100 rounded-lg p-4 mb-6">
        <p class="text-sm text-gray-600 mb-1">Waiting Time</p>
        <p class="text-3xl font-bold text-gray-900">{{ formatWaitingTime }}</p>
      </div>

      <!-- Video Feed (to show teacher you're ready) -->
      <div class="mb-6">
        <div class="relative bg-black rounded-xl overflow-hidden" style="aspect-ratio: 16/9">
          <video
            ref="videoRef"
            autoplay
            muted
            playsinline
            class="w-full h-full object-cover"
          ></video>
          <div class="absolute top-4 left-4 bg-red-500 px-3 py-1 rounded-full text-white text-sm font-semibold flex items-center gap-2">
            <span class="w-2 h-2 bg-white rounded-full animate-pulse"></span>
            PAUSED
          </div>
        </div>
        <p class="text-xs text-gray-500 mt-2">Your camera is still active for verification</p>
      </div>

      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p class="text-sm text-gray-700">
          💡 <strong>Tip:</strong> Ensure you're alone, looking at the screen, and no unauthorized materials are visible.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { io } from 'socket.io-client'
import api from '../api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const videoRef = ref(null)
const socket = ref(null)
const waitingTime = ref(0)
const suspiciousReasons = ref([])
const pausedBy = ref('the system')
const timerInterval = ref(null)
const statusCheckInterval = ref(null)
const studentStatus = ref(null)
const isInitialEntry = computed(() => pausedBy.value === 'system' && (!route.query.reasons || route.query.reasons.includes('approval')))

const formatWaitingTime = computed(() => {
  const mins = Math.floor(waitingTime.value / 60)
  const secs = waitingTime.value % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
})

// Check waiting room status with backend
const checkWaitingRoomStatus = async () => {
  try {
    const testId = route.query.testId
    const studentId = authStore.user.id
    
    const response = await api.get(`/proctoring/waiting-room-status/${testId}/${studentId}`)
    studentStatus.value = response.data
    
    console.log('Waiting room status:', response.data)
    
    if (response.data.in_waiting_room) {
      const status = response.data.status
      
      if (status === 'admitted') {
        // Teacher let student back in!
        console.log('✅ Teacher admitted student back')
        router.push(`/student/test/${testId}`)
      } else if (status === 'terminated') {
        // Teacher terminated the test
        console.log('❌ Teacher terminated test')
        alert('Your test has been terminated by the teacher.')
        router.push('/student/dashboard')
      } else if (status === 'paused') {
        pausedBy.value = 'Teacher'
      }
    }
  } catch (error) {
    console.error('Failed to check waiting room status:', error)
  }
}

const initializeCamera = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ 
      video: { facingMode: 'user' }, 
      audio: false 
    })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
    }
  } catch (error) {
    console.error('Camera error:', error)
  }
}

const connectSocket = () => {
  socket.value = io('http://localhost:8000', {
    transports: ['websocket']
  })

  socket.value.on('connect', () => {
    console.log('Waiting room socket connected')
    socket.value.emit('student_in_waiting_room', {
      test_id: route.query.testId,
      attempt_id: route.query.attemptId,
      user_id: authStore.user.id,
      name: authStore.user.full_name,
      test_code: route.query.testCode || '' // Add test code for teacher notification
    })
  })

  socket.value.on('approved_to_continue', () => {
    console.log('Approved to continue test')
    // Return to test
    router.push(`/test/${route.query.testId}`)
  })

  socket.value.on('test_terminated', (data) => {
    console.log('Test terminated:', data)
    alert('Your test has been terminated by the teacher.')
    router.push('/student/dashboard')
  })
}

onMounted(async () => {
  // Get suspension reasons from query params
  const reasons = route.query.reasons
  if (reasons) {
    suspiciousReasons.value = JSON.parse(decodeURIComponent(reasons))
  }
  
  pausedBy.value = route.query.pausedBy || 'the system'

  await initializeCamera()
  connectSocket()

  // Start waiting timer
  timerInterval.value = setInterval(() => {
    waitingTime.value++
  }, 1000)
  
  // Check waiting room status every 3 seconds
  statusCheckInterval.value = setInterval(checkWaitingRoomStatus, 3000)
  checkWaitingRoomStatus() // Check immediately
})

onUnmounted(() => {
  if (socket.value) {
    socket.value.disconnect()
  }
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
  }
  if (statusCheckInterval.value) {
    clearInterval(statusCheckInterval.value)
  }
  if (videoRef.value?.srcObject) {
    videoRef.value.srcObject.getTracks().forEach(track => track.stop())
  }
})
</script>
