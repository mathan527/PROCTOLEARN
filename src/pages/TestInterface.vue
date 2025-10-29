<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100">
    <header class="bg-white shadow-md sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">{{ test?.title || 'Loading...' }}</h1>
          <p class="text-sm text-gray-600">{{ test?.description }}</p>
        </div>
        <div class="flex items-center gap-6">
          <div class="text-center bg-red-50 px-4 py-2 rounded-lg">
            <p class="text-xs text-gray-600 mb-1">Time Remaining</p>
            <p class="text-2xl font-bold text-red-600">{{ formatTime(timeRemaining) }}</p>
          </div>
          <div class="flex flex-col gap-1 text-xs">
            <div class="flex items-center gap-2">
              <span :class="cameraActive ? 'bg-green-500' : 'bg-red-500'" class="w-2 h-2 rounded-full"></span>
              <span>Camera</span>
            </div>
            <div class="flex items-center gap-2">
              <span :class="audioLevel > 10 ? 'bg-green-500' : 'bg-gray-300'" class="w-2 h-2 rounded-full"></span>
              <span>Audio</span>
            </div>
            <div class="flex items-center gap-2" :title="getDetectionModeTooltip()">
              <span :class="getDetectionModeColor()" class="w-2 h-2 rounded-full"></span>
              <span>{{ detectionMode?.toUpperCase() || 'INIT' }}</span>
            </div>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-6 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div class="lg:col-span-3">
          <div v-if="!testStarted" class="bg-white rounded-xl shadow-lg p-8 text-center">
            <h2 class="text-2xl font-bold mb-4">Camera & Microphone Required</h2>
            <p class="text-gray-600 mb-6">This test requires continuous monitoring. Please allow camera and microphone access.</p>
            <video ref="videoRef" autoplay muted class="w-64 h-48 mx-auto mb-6 rounded-lg bg-black"></video>
            <button @click="startTest" :disabled="!cameraActive" class="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed">
              {{ cameraActive ? 'Start Test' : 'Waiting for camera...' }}
            </button>
          </div>

          <div v-else class="bg-white rounded-xl shadow-lg p-8">
            <!-- No questions warning -->
            <div v-if="questions.length === 0" class="text-center py-12">
              <div class="text-6xl mb-4">📝</div>
              <h3 class="text-2xl font-bold text-gray-900 mb-2">No Questions Available</h3>
              <p class="text-gray-600 mb-6">This test doesn't have any questions yet.</p>
              <button @click="router.push('/student/dashboard')" class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                Back to Dashboard
              </button>
            </div>

            <!-- Question content -->
            <div v-else>
              <div class="mb-6">
                <div class="flex justify-between items-center mb-2">
                  <p class="text-sm text-gray-600">Question {{ currentQuestionIndex + 1 }} of {{ questions.length }}</p>
                  <span class="text-sm font-semibold" :class="answers[currentQuestion?.id] ? 'text-green-600' : 'text-gray-400'">
                    {{ answers[currentQuestion?.id] ? 'Answered' : 'Not Answered' }}
                  </span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div class="bg-blue-600 h-2 rounded-full transition-all" :style="{ width: progress + '%' }"></div>
                </div>
              </div>

            <!-- Question text -->
            <div class="mb-6">
              <h2 class="text-xl font-bold text-gray-900">{{ currentQuestion?.question_text }}</h2>
              <img v-if="currentQuestion?.question_image_url" 
                :src="currentQuestion.question_image_url" 
                alt="Question image" 
                class="mt-4 max-w-md rounded-lg shadow-md" />
            </div>

            <div v-if="currentQuestion?.question_type === 'multiple_choice'" class="space-y-3">
              <label v-for="(option, idx) in currentQuestion.options" :key="idx" 
                class="flex items-start p-4 border-2 rounded-lg cursor-pointer transition-all"
                :class="answers[currentQuestion.id] === option ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-300'">
                <input type="radio" :value="option" v-model="answers[currentQuestion.id]" class="mt-1 mr-3" />
                <span class="text-gray-800">{{ option }}</span>
              </label>
            </div>

            <div v-else-if="currentQuestion?.question_type === 'true_false'" class="space-y-3">
              <label class="flex items-start p-4 border-2 rounded-lg cursor-pointer transition-all"
                :class="answers[currentQuestion.id] === 'true' ? 'border-green-500 bg-green-50' : 'border-gray-200 hover:border-green-300'">
                <input type="radio" value="true" v-model="answers[currentQuestion.id]" class="mt-1 mr-3" />
                <span class="text-gray-800 font-semibold">✓ True</span>
              </label>
              <label class="flex items-start p-4 border-2 rounded-lg cursor-pointer transition-all"
                :class="answers[currentQuestion.id] === 'false' ? 'border-red-500 bg-red-50' : 'border-gray-200 hover:border-red-300'">
                <input type="radio" value="false" v-model="answers[currentQuestion.id]" class="mt-1 mr-3" />
                <span class="text-gray-800 font-semibold">✗ False</span>
              </label>
            </div>

            <div v-else-if="currentQuestion?.question_type === 'short_answer'" class="space-y-3">
              <textarea v-model="answers[currentQuestion.id]" 
                class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none" 
                rows="4"
                placeholder="Type your answer here..."></textarea>
            </div>

            <div v-else-if="currentQuestion?.question_type === 'essay'" class="space-y-3">
              <textarea v-model="answers[currentQuestion.id]" 
                class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none" 
                rows="12"
                placeholder="Write your essay here..."></textarea>
            </div>

            <div class="flex justify-between mt-8 pt-6 border-t">
              <button @click="previousQuestion" :disabled="currentQuestionIndex === 0" 
                class="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed">
                Previous
              </button>
              <button v-if="currentQuestionIndex === questions.length - 1" @click="confirmSubmit" 
                class="px-8 py-2 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700">
                Submit Test
              </button>
              <button v-else @click="nextQuestion" 
                class="px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700">
                Next
              </button>
            </div>
            </div>
          </div>
        </div>

        <div class="space-y-4">
          <div class="bg-white rounded-xl shadow-lg p-4">
            <h3 class="font-bold mb-3 text-gray-900">Questions</h3>
            <div class="grid grid-cols-5 gap-2">
              <button v-for="(q, idx) in questions" :key="q.id" @click="currentQuestionIndex = idx" 
                :class="[
                  'aspect-square rounded-lg text-sm font-semibold transition-all',
                  idx === currentQuestionIndex ? 'bg-blue-600 text-white' : 
                  answers[q.id] ? 'bg-green-200 text-green-800 hover:bg-green-300' : 
                  'bg-gray-200 text-gray-600 hover:bg-gray-300'
                ]">
                {{ idx + 1 }}
              </button>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-lg p-4 border-2 border-yellow-400">
            <h3 class="font-bold mb-3 text-gray-900 flex items-center gap-2">
              <span class="text-yellow-600">⚠️</span> Monitoring
            </h3>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between items-center">
                <span class="text-gray-600">Tab Switches</span>
                <span class="font-bold text-red-600">{{ tabSwitches }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-gray-600">Violations</span>
                <span class="font-bold text-red-600">{{ violationCount }}</span>
              </div>
            </div>
          </div>

          <div v-if="recentViolations.length > 0" class="bg-red-50 rounded-xl shadow-lg p-4 border-2 border-red-300">
            <h3 class="font-bold mb-3 text-red-700 flex items-center gap-2">
              <span>🚨</span> Recent Alerts
            </h3>
            <div class="space-y-2 text-xs max-h-40 overflow-y-auto">
              <div v-for="(violation, idx) in recentViolations" :key="idx" class="text-red-600 py-1 border-b border-red-200 last:border-0">
                {{ violation.details }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- AI Monitoring Notification Popup -->
    <Transition name="slide-down">
      <div v-if="showMonitoringNotification" 
           class="fixed top-20 right-6 z-50 max-w-sm bg-white rounded-lg shadow-2xl border-2 p-4"
           :class="{
             'border-blue-500': notificationType === 'info',
             'border-green-500': notificationType === 'success',
             'border-red-500': notificationType === 'error'
           }">
        <div class="flex items-start gap-3">
          <div class="flex-shrink-0">
            <div v-if="notificationType === 'info'" class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div v-else-if="notificationType === 'success'" class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div v-else class="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <div class="flex-1">
            <h4 class="font-bold text-gray-900 mb-1">AI Proctoring</h4>
            <p class="text-sm text-gray-600">{{ notificationMessage }}</p>
          </div>
          <button @click="showMonitoringNotification = false" class="flex-shrink-0 text-gray-400 hover:text-gray-600">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </Transition>

    <!-- Camera Monitoring Overlay (Miniature) -->
    <div v-if="testStarted && cameraActive" class="fixed bottom-6 right-6 z-40">
      <div class="relative w-48 h-36 bg-black rounded-lg shadow-2xl overflow-hidden border-4"
           :class="{
             'border-green-500': faceDetectionStatus?.faceDetected && faceDetectionStatus?.eyesOpen && faceDetectionStatus?.lookingAtScreen,
             'border-yellow-500': faceDetectionStatus?.faceDetected && (!faceDetectionStatus?.eyesOpen || !faceDetectionStatus?.lookingAtScreen),
             'border-red-500': !faceDetectionStatus?.faceDetected
           }">
        <!-- Video Feed -->
        <video ref="miniVideoRef" autoplay muted playsinline class="w-full h-full object-cover"></video>
        
        <!-- Face Detection Overlay Lines -->
        <svg v-if="faceDetectionStatus?.faceBoundingBox" 
             class="absolute inset-0 w-full h-full pointer-events-none"
             viewBox="0 0 640 480"
             preserveAspectRatio="xMidYMid slice">
          <!-- Face bounding box with animated corners -->
          <g :transform="`translate(${faceDetectionStatus.faceBoundingBox.x}, ${faceDetectionStatus.faceBoundingBox.y})`">
            <!-- Top-left corner -->
            <line x1="0" y1="0" x2="30" y2="0" 
                  :class="faceDetectionStatus.faceDetected ? 'stroke-green-400' : 'stroke-red-400'" 
                  stroke-width="3" stroke-linecap="round" />
            <line x1="0" y1="0" x2="0" y2="30" 
                  :class="faceDetectionStatus.faceDetected ? 'stroke-green-400' : 'stroke-red-400'" 
                  stroke-width="3" stroke-linecap="round" />
            
            <!-- Top-right corner -->
            <line :x1="faceDetectionStatus.faceBoundingBox.width - 30" y1="0" 
                  :x2="faceDetectionStatus.faceBoundingBox.width" y2="0" 
                  :class="faceDetectionStatus.faceDetected ? 'stroke-blue-400' : 'stroke-red-400'" 
                  stroke-width="3" stroke-linecap="round" />
            <line :x1="faceDetectionStatus.faceBoundingBox.width" y1="0" 
                  :x2="faceDetectionStatus.faceBoundingBox.width" y2="30" 
                  :class="faceDetectionStatus.faceDetected ? 'stroke-blue-400' : 'stroke-red-400'" 
                  stroke-width="3" stroke-linecap="round" />
            
            <!-- Bottom-left corner -->
            <line x1="0" :y1="faceDetectionStatus.faceBoundingBox.height - 30" 
                  x2="0" :y2="faceDetectionStatus.faceBoundingBox.height" 
                  :class="faceDetectionStatus.faceDetected ? 'stroke-green-400' : 'stroke-red-400'" 
                  stroke-width="3" stroke-linecap="round" />
            <line x1="0" :y1="faceDetectionStatus.faceBoundingBox.height" 
                  x2="30" :y2="faceDetectionStatus.faceBoundingBox.height" 
                  :class="faceDetectionStatus.faceDetected ? 'stroke-green-400' : 'stroke-red-400'" 
                  stroke-width="3" stroke-linecap="round" />
            
            <!-- Bottom-right corner -->
            <line :x1="faceDetectionStatus.faceBoundingBox.width - 30" 
                  :y1="faceDetectionStatus.faceBoundingBox.height" 
                  :x2="faceDetectionStatus.faceBoundingBox.width" 
                  :y2="faceDetectionStatus.faceBoundingBox.height" 
                  :class="faceDetectionStatus.faceDetected ? 'stroke-blue-400' : 'stroke-red-400'" 
                  stroke-width="3" stroke-linecap="round" />
            <line :x1="faceDetectionStatus.faceBoundingBox.width" 
                  :y1="faceDetectionStatus.faceBoundingBox.height - 30" 
                  :x2="faceDetectionStatus.faceBoundingBox.width" 
                  :y2="faceDetectionStatus.faceBoundingBox.height" 
                  :class="faceDetectionStatus.faceDetected ? 'stroke-blue-400' : 'stroke-red-400'" 
                  stroke-width="3" stroke-linecap="round" />
          </g>
        </svg>
        
        <!-- Status Indicators -->
        <div class="absolute bottom-2 left-2 right-2 flex justify-between text-xs">
          <div class="bg-black bg-opacity-70 px-2 py-1 rounded flex items-center gap-1">
            <span :class="faceDetectionStatus?.faceDetected ? 'text-green-400' : 'text-red-400'">●</span>
            <span class="text-white">Face</span>
          </div>
          <div class="bg-black bg-opacity-70 px-2 py-1 rounded flex items-center gap-1">
            <span :class="faceDetectionStatus?.eyesOpen ? 'text-green-400' : 'text-yellow-400'">●</span>
            <span class="text-white">Eyes</span>
          </div>
          <div class="bg-black bg-opacity-70 px-2 py-1 rounded flex items-center gap-1">
            <span :class="faceDetectionStatus?.lookingAtScreen ? 'text-green-400' : 'text-yellow-400'">●</span>
            <span class="text-white">Focus</span>
          </div>
        </div>
        
        <!-- AI Active Badge -->
        <div class="absolute top-2 left-2 bg-red-600 text-white text-xs px-2 py-1 rounded flex items-center gap-1 animate-pulse">
          <span class="w-2 h-2 bg-white rounded-full"></span>
          <span class="font-bold">AI MONITORING</span>
        </div>
      </div>
    </div>

    <!-- Monitoring Notifications -->
    <Transition name="slide-down">
      <div v-if="showMonitoringNotification" 
           class="fixed top-20 left-1/2 transform -translate-x-1/2 z-50">
        <div :class="[
          'px-6 py-4 rounded-lg shadow-2xl border-2 flex items-center gap-3',
          notificationType === 'success' ? 'bg-green-50 border-green-500' :
          notificationType === 'error' ? 'bg-red-50 border-red-500' :
          'bg-blue-50 border-blue-500'
        ]">
          <span class="text-2xl">
            {{ notificationType === 'success' ? '✓' : 
               notificationType === 'error' ? '✗' : 'ℹ️' }}
          </span>
          <span class="font-semibold">{{ notificationMessage }}</span>
        </div>
      </div>
    </Transition>

    <!-- Mini Camera Preview with Face Detection Overlay -->
    <div v-if="testStarted" 
         class="fixed bottom-4 right-4 w-64 h-48 rounded-lg overflow-hidden border-2 shadow-2xl bg-black z-40"
         :class="faceDetectionStatus?.faceDetected ? 'border-green-500' : 'border-red-500'">
      <video ref="miniVideoRef" autoplay muted playsinline 
             class="w-full h-full object-cover"></video>
      
      <!-- Face detection box overlay with scanning lines -->
      <canvas ref="faceOverlayCanvas" 
              class="absolute inset-0 pointer-events-none"
              width="256" height="192"></canvas>
      
      <!-- Status indicator -->
      <div class="absolute top-2 left-2 px-2 py-1 rounded text-xs font-bold text-white"
           :class="faceDetectionStatus?.faceDetected ? 'bg-green-500' : 'bg-red-500'">
        {{ faceDetectionStatus?.faceDetected ? '✓ Face Detected' : '✗ No Face' }}
      </div>

      <!-- Scanning line animation -->
      <div v-if="faceDetectionStatus?.faceDetected" class="absolute inset-0 pointer-events-none overflow-hidden">
        <div class="scan-line"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.slide-down-enter-active, .slide-down-leave-active {
  transition: all 0.3s ease;
}
.slide-down-enter-from {
  transform: translate(-50%, -100%);
  opacity: 0;
}
.slide-down-leave-to {
  transform: translate(-50%, -100%);
  opacity: 0;
}

.scan-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #10b981, transparent);
  animation: scan 2s linear infinite;
}

@keyframes scan {
  0% {
    top: 0;
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
  100% {
    top: 100%;
    opacity: 0;
  }
}
</style>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useProctoring } from '../composables/useProctoring'
import { io } from 'socket.io-client'
import api from '../api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const test = ref(null)
const attempt = ref(null)
const questions = ref([])
const currentQuestionIndex = ref(0)
const answers = ref({})
const timeRemaining = ref(0)
const testStarted = ref(false)
const cameraActive = ref(false)
const tabSwitches = ref(0)
const violationCount = ref(0)
const recentViolations = ref([])
const socket = ref(null)
const screenVideoRef = ref(null)
const screenCanvasRef = ref(null)
const cameraPeerConnection = ref(null)
const screenPeerConnection = ref(null)
const miniVideoRef = ref(null)
const faceOverlayCanvas = ref(null)

// Monitoring notification state
const showMonitoringNotification = ref(false)
const notificationMessage = ref('')
const notificationType = ref('info') // 'info', 'success', 'error'
let notificationTimeout = null

// Show monitoring notification function
const showNotification = (message, type = 'info', duration = 3000) => {
  showMonitoringNotification.value = true
  notificationMessage.value = message
  notificationType.value = type
  
  if (notificationTimeout) {
    clearTimeout(notificationTimeout)
  }
  
  notificationTimeout = setTimeout(() => {
    showMonitoringNotification.value = false
  }, duration)
}

// Expose notification function to window for useProctoring
if (typeof window !== 'undefined') {
  window.showMonitoringNotification = showNotification
}

const currentQuestion = computed(() => {
  const question = questions.value[currentQuestionIndex.value]
  if (question) {
    console.log('Current question:', question)
  }
  return question
})
const progress = computed(() => ((currentQuestionIndex.value + 1) / questions.value.length) * 100)

const { videoRef, audioLevel, detectionMode, modelStatus, faceDetectionStatus, initializeCamera, captureFrame, cleanup } = useProctoring(async (violation) => {
  violationCount.value++
  recentViolations.value.unshift({
    ...violation,
    timestamp: new Date().toISOString()
  })
  if (recentViolations.value.length > 5) {
    recentViolations.value.pop()
  }

  // Check if student should be sent to waiting room
  if (violation.action === 'waiting_room') {
    console.log('🚨 CRITICAL: Sending student to waiting room')
    
    try {
      // Call backend to register in waiting room
      await api.post('/proctoring/send-to-waiting-room', {
        attempt_id: attempt.value?.id,
        violation_type: violation.type,
        severity: 'critical',
        violation_score: violation.score || violationCount.value,
        details: violation.details
      })
      
      console.log('✅ Backend: Student registered in waiting room')
    } catch (error) {
      console.error('❌ Failed to register in waiting room:', error)
    }
    
    // Notify teacher via socket
    if (socket.value?.connected) {
      socket.value.emit('student_flagged', {
        type: 'severe_violations',
        severity: 'critical',
        details: violation.details,
        reasons: violation.reasons,
        score: violation.score || violationCount.value
      })
    }
    
    // Redirect to waiting room with test code
    const reasonsParam = encodeURIComponent(JSON.stringify(violation.reasons))
    router.push(`/waiting-room?testId=${test.value.id}&attemptId=${attempt.value?.id}&testCode=${test.value.test_code}&reasons=${reasonsParam}&pausedBy=AI Detection System`)
    return
  }

  // Normal violation handling - report to backend
  try {
    await api.post('/proctoring/report-violation', {
      attempt_id: attempt.value?.id,
      violation_type: violation.type,
      severity: violation.severity || 'medium',
      violation_score: 1,
      details: violation.details || violation.type
    })
  } catch (error) {
    console.error('Failed to report violation:', error)
  }

  if (socket.value?.connected) {
    socket.value.emit('violation_detected', {
      type: violation.type,
      severity: violation.severity,
      details: violation.details,
      timestamp: new Date().toISOString()
    })
  }
})

// Draw face detection overlay
watch(() => faceDetectionStatus.value?.faceBoundingBox, (box) => {
  if (!box || !faceOverlayCanvas.value) return
  
  const canvas = faceOverlayCanvas.value
  const ctx = canvas.getContext('2d')
  const videoEl = miniVideoRef.value
  
  if (!videoEl || !ctx) return
  
  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  // Scale box coordinates to canvas size
  const scaleX = canvas.width / videoEl.videoWidth
  const scaleY = canvas.height / videoEl.videoHeight
  
  const scaledBox = {
    x: box.x * scaleX,
    y: box.y * scaleY,
    width: box.width * scaleX,
    height: box.height * scaleY
  }
  
  // Draw box with green (looking) or blue (not looking)
  ctx.strokeStyle = faceDetectionStatus.value?.lookingAtScreen ? '#10b981' : '#3b82f6'
  ctx.lineWidth = 2
  ctx.strokeRect(scaledBox.x, scaledBox.y, scaledBox.width, scaledBox.height)
  
  // Draw corner markers
  const cornerSize = 15
  ctx.lineWidth = 3
  
  // Top-left
  ctx.beginPath()
  ctx.moveTo(scaledBox.x, scaledBox.y + cornerSize)
  ctx.lineTo(scaledBox.x, scaledBox.y)
  ctx.lineTo(scaledBox.x + cornerSize, scaledBox.y)
  ctx.stroke()
  
  // Top-right
  ctx.beginPath()
  ctx.moveTo(scaledBox.x + scaledBox.width - cornerSize, scaledBox.y)
  ctx.lineTo(scaledBox.x + scaledBox.width, scaledBox.y)
  ctx.lineTo(scaledBox.x + scaledBox.width, scaledBox.y + cornerSize)
  ctx.stroke()
  
  // Bottom-left
  ctx.beginPath()
  ctx.moveTo(scaledBox.x, scaledBox.y + scaledBox.height - cornerSize)
  ctx.lineTo(scaledBox.x, scaledBox.y + scaledBox.height)
  ctx.lineTo(scaledBox.x + cornerSize, scaledBox.y + scaledBox.height)
  ctx.stroke()
  
  // Bottom-right
  ctx.beginPath()
  ctx.moveTo(scaledBox.x + scaledBox.width - cornerSize, scaledBox.y + scaledBox.height)
  ctx.lineTo(scaledBox.x + scaledBox.width, scaledBox.y + scaledBox.height)
  ctx.lineTo(scaledBox.x + scaledBox.width, scaledBox.y + scaledBox.height - cornerSize)
  ctx.stroke()
}, { deep: true })

// Sync mini video with main video stream
watch(() => videoRef.value?.srcObject, (newStream) => {
  if (miniVideoRef.value && newStream) {
    miniVideoRef.value.srcObject = newStream
  }
})

// Screen capture function
const captureScreenFrame = () => {
  if (!screenVideoRef.value || !screenCanvasRef.value) return null
  
  try {
    const video = screenVideoRef.value
    const canvas = screenCanvasRef.value
    const ctx = canvas.getContext('2d')
    
    canvas.width = video.videoWidth || 640
    canvas.height = video.videoHeight || 480
    
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    return canvas.toDataURL('image/jpeg', 0.5)
  } catch (error) {
    console.error('Error capturing screen frame:', error)
    return null
  }
}

// Initialize screen share
const initializeScreenShare = async () => {
  try {
    const stream = await navigator.mediaDevices.getDisplayMedia({
      video: {
        cursor: 'always',
        displaySurface: 'monitor'
      }
    })
    
    screenVideoRef.value = document.createElement('video')
    screenVideoRef.value.srcObject = stream
    screenVideoRef.value.play()
    
    screenCanvasRef.value = document.createElement('canvas')
    
    return true
  } catch (error) {
    console.error('Failed to initialize screen share:', error)
    return false
  }
}

const setupWebRTCStream = async (streamType) => {
  try {
    console.log(`Setting up WebRTC for ${streamType}`)
    
    // Get the appropriate stream first
    let stream
    let maxRetries = 10
    let retryCount = 0
    
    // Wait for stream to be available
    while (!stream && retryCount < maxRetries) {
      if (streamType === 'camera' && videoRef.value && videoRef.value.srcObject) {
        stream = videoRef.value.srcObject
        console.log('Camera stream found with tracks:', stream.getTracks().length)
      } else if (streamType === 'screen' && screenVideoRef.value && screenVideoRef.value.srcObject) {
        stream = screenVideoRef.value.srcObject
        console.log('Screen stream found with tracks:', stream.getTracks().length)
      }
      
      if (!stream) {
        console.log(`Waiting for ${streamType} stream... (${retryCount + 1}/${maxRetries})`)
        await new Promise(resolve => setTimeout(resolve, 500))
        retryCount++
      }
    }
    
    if (!stream) {
      console.error(`No ${streamType} stream available after ${maxRetries} retries`)
      return
    }

    // Verify stream has active tracks
    const activeTracks = stream.getTracks().filter(track => track.readyState === 'live')
    if (activeTracks.length === 0) {
      console.error(`${streamType} stream has no active tracks`)
      return
    }
    
    console.log(`${streamType} stream ready with ${activeTracks.length} active tracks`)
    
    // Create peer connection
    const pc = new RTCPeerConnection({
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' },
        { urls: 'stun:stun2.l.google.com:19302' }
      ],
      iceCandidatePoolSize: 10
    })
    
    // Store peer connection
    if (streamType === 'camera') {
      cameraPeerConnection.value = pc
    } else {
      screenPeerConnection.value = pc
    }
    
    // Add tracks to peer connection
    activeTracks.forEach(track => {
      pc.addTrack(track, stream)
      console.log(`Added ${track.kind} track (${track.id}) to ${streamType} peer connection`)
    })
    
    // Create DataChannel for audio levels (only for camera stream)
    if (streamType === 'camera') {
      const dataChannel = pc.createDataChannel('audioLevels')
      dataChannel.onopen = () => {
        console.log('Audio level DataChannel opened')
        // Send audio levels every 2 seconds via DataChannel
        const audioInterval = setInterval(() => {
          if (dataChannel.readyState === 'open') {
            dataChannel.send(JSON.stringify({
              level: audioLevel.value,
              timestamp: Date.now()
            }))
          } else {
            clearInterval(audioInterval)
          }
        }, 2000)
        // Store interval for cleanup
        pc.audioInterval = audioInterval
      }
      dataChannel.onerror = (error) => {
        console.error('DataChannel error:', error)
      }
    }
    
    // Handle ICE candidates
    pc.onicecandidate = (event) => {
      if (event.candidate && socket.value?.connected) {
        socket.value.emit('webrtc_ice_candidate', {
          candidate: event.candidate,
          stream_type: streamType
        })
        console.log(`Sent ICE candidate for ${streamType}`)
      }
    }
    
    // Monitor connection state
    pc.onconnectionstatechange = () => {
      console.log(`${streamType} connection state:`, pc.connectionState)
      if (pc.connectionState === 'failed') {
        console.error(`${streamType} connection failed, attempting restart...`)
        // Attempt to restart ICE
        pc.restartIce()
      }
    }
    
    pc.oniceconnectionstatechange = () => {
      console.log(`${streamType} ICE connection state:`, pc.iceConnectionState)
    }
    
    // Create and send offer
    const offer = await pc.createOffer({
      offerToReceiveAudio: false,
      offerToReceiveVideo: false
    })
    await pc.setLocalDescription(offer)
    
    if (socket.value?.connected) {
      socket.value.emit('webrtc_offer', {
        offer: offer,
        stream_type: streamType
      })
      console.log(`Sent WebRTC offer for ${streamType}`)
    } else {
      console.error('Socket not connected, cannot send WebRTC offer')
    }
    
  } catch (error) {
    console.error(`Failed to setup WebRTC for ${streamType}:`, error)
  }
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const loadTest = async () => {
  try {
    const testId = route.params.testId
    console.log('Loading test with ID:', testId)
    const response = await api.get(`/tests/${testId}`)
    console.log('Test loaded:', response.data)
    console.log('Questions:', response.data.questions)
    test.value = response.data
    questions.value = response.data.questions || []
    console.log('Questions array length:', questions.value.length)
    timeRemaining.value = (test.value.duration_minutes || 60) * 60
  } catch (error) {
    console.error('Failed to load test:', error)
    router.push('/student/dashboard')
  }
}

const startTest = async () => {
  try {
    // Check if we already have an attempt ID from TestJoinPage
    const existingAttemptId = sessionStorage.getItem('attemptId')
    
    if (existingAttemptId) {
      // Use existing attempt
      attempt.value = { id: parseInt(existingAttemptId), test_id: test.value.id }
      testStarted.value = true
    } else {
      // Create new attempt (fallback for direct access)
      const response = await api.post('/tests/start', {
        test_code: test.value.test_code
      })
      attempt.value = response.data
      testStarted.value = true
    }

    // Always initialize screen share for streaming
    await initializeScreenShare()

    socket.value = io('http://localhost:8000', {
      transports: ['websocket']
    })

    socket.value.on('connect', () => {
      console.log('✅ Socket connected, joining as student')
      socket.value.emit('join_test_as_student', {
        test_code: test.value.test_code,
        user_id: authStore.user.id,
        name: authStore.user.full_name,
        attempt_id: attempt.value.id
      })
      
      console.log('📡 Joined test room:', test.value.test_code)
    })

    socket.value.on('joined_test', async (data) => {
      console.log('Successfully joined test:', data)
      
      // Enter fullscreen mode
      enterFullscreen()
      
      // Initialize camera first (from useProctoring)
      console.log('Initializing camera from useProctoring...')
      await initializeCamera()
      
      // Wait for video element to be ready
      await new Promise((resolve) => {
        if (videoRef.value && videoRef.value.readyState >= 2) {
          resolve()
        } else if (videoRef.value) {
          videoRef.value.addEventListener('loadeddata', resolve, { once: true })
          // Fallback timeout
          setTimeout(resolve, 3000)
        } else {
          setTimeout(resolve, 3000)
        }
      })
      
      console.log('Camera initialized, setting up WebRTC streams...')
      
      // Set up WebRTC for camera stream
      await setupWebRTCStream('camera')
      
      // Set up WebRTC for screen stream  
      await setupWebRTCStream('screen')
      
      console.log('WebRTC setup complete')
    })

    socket.value.on('webrtc_answer', async (data) => {
      console.log('📥 Received WebRTC answer for:', data.stream_type)
      
      const pc = data.stream_type === 'camera' ? cameraPeerConnection.value : screenPeerConnection.value
      if (pc && data.answer) {
        await pc.setRemoteDescription(new RTCSessionDescription(data.answer))
      }
    })

    socket.value.on('webrtc_ice_candidate', async (data) => {
      console.log('📥 Received ICE candidate for:', data.stream_type)
      
      const pc = data.stream_type === 'camera' ? cameraPeerConnection.value : screenPeerConnection.value
      if (pc && data.candidate) {
        await pc.addIceCandidate(new RTCIceCandidate(data.candidate))
      }
    })

    socket.value.on('error', (error) => {
      console.error('❌ Socket error:', error)
    })

    // Timer interval for test countdown
    const timerInterval = setInterval(() => {
      timeRemaining.value--
      if (timeRemaining.value <= 0) {
        clearInterval(timerInterval)
        submitTest()
      }
    }, 1000)
  } catch (error) {
    console.error('Failed to start test:', error)
  }
}

const nextQuestion = () => {
  if (currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value++
  }
}

const previousQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
  }
}

const confirmSubmit = () => {
  const unanswered = questions.value.filter(q => !answers.value[q.id]).length
  if (unanswered > 0) {
    if (!confirm(`You have ${unanswered} unanswered questions. Submit anyway?`)) {
      return
    }
  }
  submitTest()
}

const submitTest = async () => {
  try {
    const submissionData = questions.value.map(q => ({
      question_id: q.id,
      answer_text: answers.value[q.id] || '',
      attempt_id: attempt.value.id
    }))

    await api.post(`/questions/submit-test/${attempt.value.id}`, {
      answers: submissionData
    })

    if (socket.value) {
      socket.value.disconnect()
    }

    router.push('/student/dashboard')
  } catch (error) {
    console.error('Failed to submit test:', error)
  }
}

const handleVisibilityChange = () => {
  if (document.hidden && testStarted.value) {
    tabSwitches.value++
    violationCount.value++
    recentViolations.value.unshift({
      type: 'tab_switch',
      severity: 'high',
      details: 'Tab switch detected',
      timestamp: new Date().toISOString()
    })

    if (socket.value?.connected) {
      socket.value.emit('violation_detected', {
        type: 'tab_switch',
        severity: 'high',
        details: 'Student switched tabs',
        timestamp: new Date().toISOString()
      })
    }
  }
}

const handleWindowBlur = () => {
  if (testStarted.value) {
    console.log('⚠️ Window lost focus')
  }
}

const handleWindowFocus = () => {
  if (testStarted.value) {
    console.log('✅ Window regained focus')
  }
}

const preventFocusLoss = (e) => {
  if (testStarted.value) {
    // Prevent certain actions that might cause focus loss
    if (e.target.tagName === 'A' && e.target.target === '_blank') {
      e.preventDefault()
      console.warn('⚠️ Opening new windows is blocked during test')
    }
  }
}

const enterFullscreen = async () => {
  try {
    const elem = document.documentElement
    if (elem.requestFullscreen) {
      await elem.requestFullscreen()
    } else if (elem.webkitRequestFullscreen) {
      await elem.webkitRequestFullscreen()
    } else if (elem.mozRequestFullScreen) {
      await elem.mozRequestFullScreen()
    } else if (elem.msRequestFullscreen) {
      await elem.msRequestFullscreen()
    }
    console.log('✅ Entered fullscreen mode')
  } catch (error) {
    console.error('❌ Failed to enter fullscreen:', error)
  }
}

const handleFullscreenChange = () => {
  if (testStarted.value) {
    const isFullscreen = document.fullscreenElement || 
                        document.webkitFullscreenElement || 
                        document.mozFullScreenElement || 
                        document.msFullscreenElement
    
    if (!isFullscreen) {
      console.log('🚨 Student exited fullscreen - sending to waiting room')
      
      // Notify via socket
      if (socket.value?.connected) {
        socket.value.emit('student_flagged', {
          type: 'fullscreen_exit',
          severity: 'critical',
          details: 'Student exited fullscreen mode'
        })
      }
      
      // Redirect to waiting room
      router.push(`/waiting-room?testId=${test.value.id}&attemptId=${attempt.value.id}&testCode=${test.value.test_code}&reasons=${encodeURIComponent(JSON.stringify(['Exited fullscreen mode']))}&pausedBy=Proctoring System`)
    }
  }
}

const getDetectionModeColor = () => {
  if (!detectionMode.value) return 'bg-gray-400'
  
  switch (detectionMode.value) {
    case 'full':
      return 'bg-green-500'
    case 'basic':
      return 'bg-yellow-500'
    case 'manual':
      return 'bg-orange-500'
    default:
      return 'bg-gray-400'
  }
}

const getDetectionModeTooltip = () => {
  if (!detectionMode.value) return 'Initializing ML models...'
  
  const loadedModels = modelStatus.value ? 
    Object.entries(modelStatus.value)
      .filter(([_, status]) => status.loaded)
      .map(([name]) => name)
      .join(', ') 
    : 'none'
  
  switch (detectionMode.value) {
    case 'full':
      return `FULL Detection: All ML models active (${loadedModels})`
    case 'basic':
      return `BASIC Detection: Limited ML models (${loadedModels})`
    case 'manual':
      return `MANUAL Detection: Using fallback methods (tab/window tracking only)`
    default:
      return 'Detection mode unknown'
  }
}

onMounted(async () => {
  await loadTest()
  
  cameraActive.value = await initializeCamera()
  
  // Auto-start if coming from TestJoinPage (streams already setup)
  const hasExistingAttempt = sessionStorage.getItem('attemptId')
  const hasCameraStream = sessionStorage.getItem('cameraStream')
  const hasScreenStream = sessionStorage.getItem('screenStream')
  
  if (hasExistingAttempt && hasCameraStream && hasScreenStream && cameraActive.value) {
    // Automatically start the test since setup is already done
    await startTest()
  }
  
  document.addEventListener('visibilitychange', handleVisibilityChange)
  window.addEventListener('blur', handleWindowBlur)
  window.addEventListener('focus', handleWindowFocus)
  document.addEventListener('click', preventFocusLoss, true)
  
  // Fullscreen change detection
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.addEventListener('mozfullscreenchange', handleFullscreenChange)
  document.addEventListener('MSFullscreenChange', handleFullscreenChange)
  
  window.addEventListener('beforeunload', (e) => {
    if (testStarted.value) {
      e.preventDefault()
      e.returnValue = ''
    }
  })
})

// Sync mini video with main video stream
watch(videoRef, (newVideo) => {
  if (newVideo && newVideo.srcObject && miniVideoRef.value) {
    miniVideoRef.value.srcObject = newVideo.srcObject
  }
}, { immediate: true })

onUnmounted(() => {
  cleanup()
  
  // Clean up peer connections and their intervals
  if (cameraPeerConnection.value) {
    if (cameraPeerConnection.value.audioInterval) {
      clearInterval(cameraPeerConnection.value.audioInterval)
    }
    cameraPeerConnection.value.close()
  }
  if (screenPeerConnection.value) {
    screenPeerConnection.value.close()
  }
  
  if (socket.value) {
    socket.value.disconnect()
  }
  
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  window.removeEventListener('blur', handleWindowBlur)
  window.removeEventListener('focus', handleWindowFocus)
  document.removeEventListener('click', preventFocusLoss, true)
  
  // Remove fullscreen listeners
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.removeEventListener('mozfullscreenchange', handleFullscreenChange)
  document.removeEventListener('MSFullscreenChange', handleFullscreenChange)
})
</script>

<style scoped>
/* Slide down transition for notification */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  transform: translateY(-100%);
  opacity: 0;
}

.slide-down-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}
</style>
