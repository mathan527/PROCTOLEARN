<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
    <!-- Header -->
    <header class="bg-white shadow-md">
      <div class="max-w-7xl mx-auto px-8 py-4">
        <h1 class="text-2xl font-bold text-indigo-600">🎓 Join Proctored Test</h1>
      </div>
    </header>

    <div class="max-w-4xl mx-auto px-6 py-12">
      <!-- Step 1: Enter Test Code -->
      <div v-if="step === 1" class="bg-white rounded-2xl shadow-xl p-8">
        <div class="text-center mb-8">
          <div class="text-6xl mb-4">🔐</div>
          <h2 class="text-3xl font-bold text-gray-900 mb-2">Enter Test Code</h2>
          <p class="text-gray-600">Your teacher will provide you with a 4-digit code</p>
        </div>

        <form @submit.prevent="validateCode" class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-3 text-center">
              Test Code
            </label>
            <div class="flex justify-center gap-3">
              <input
                v-for="(digit, index) in testCode"
                :key="index"
                :ref="el => codeInputs[index] = el"
                v-model="testCode[index]"
                @input="handleCodeInput(index, $event)"
                @keydown="handleKeyDown(index, $event)"
                type="text"
                maxlength="1"
                class="w-16 h-20 text-center text-3xl font-bold border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                pattern="[0-9]"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            :disabled="loading || testCode.join('').length !== 4"
            class="w-full px-6 py-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-semibold text-lg"
          >
            <span v-if="loading">Validating...</span>
            <span v-else>Continue →</span>
          </button>
        </form>
      </div>

      <!-- Step 2: Setup Camera & Screen Share -->
      <div v-else-if="step === 2" class="bg-white rounded-2xl shadow-xl p-8">
        <div class="text-center mb-8">
          <div class="text-6xl mb-4">🎥</div>
          <h2 class="text-3xl font-bold text-gray-900 mb-2">Setup Monitoring</h2>
          <p class="text-gray-600">Enable camera and screen sharing for proctoring</p>
        </div>

        <!-- Test Info -->
        <div class="bg-indigo-50 border-2 border-indigo-200 rounded-xl p-6 mb-8">
          <h3 class="font-bold text-lg text-gray-900 mb-2">{{ testInfo.title }}</h3>
          <div class="grid md:grid-cols-3 gap-4 text-sm">
            <div>
              <span class="text-gray-600">Duration:</span>
              <span class="font-semibold ml-2">{{ testInfo.duration_minutes }} min</span>
            </div>
            <div>
              <span class="text-gray-600">Total Marks:</span>
              <span class="font-semibold ml-2">{{ testInfo.total_marks }}</span>
            </div>
            <div>
              <span class="text-gray-600">Questions:</span>
              <span class="font-semibold ml-2">{{ testInfo.question_count }}</span>
            </div>
          </div>
        </div>

        <!-- Camera Preview -->
        <div class="mb-6">
          <div class="flex items-center justify-between mb-3">
            <h4 class="font-semibold text-gray-900">📹 Camera Feed</h4>
            <span
              class="px-3 py-1 rounded-full text-sm font-semibold"
              :class="cameraEnabled ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
            >
              {{ cameraEnabled ? '✓ Active' : '✗ Inactive' }}
            </span>
          </div>
          <div class="relative bg-black rounded-xl overflow-hidden" style="aspect-ratio: 16/9">
            <video
              ref="cameraVideo"
              autoplay
              muted
              playsinline
              class="w-full h-full object-cover"
            ></video>
            <div v-if="!cameraEnabled" class="absolute inset-0 flex items-center justify-center bg-gray-800">
              <div class="text-center text-white">
                <p class="text-xl mb-2">Camera not enabled</p>
                <p class="text-sm text-gray-400">Click button below to enable</p>
              </div>
            </div>
            <!-- Face Detection Indicator -->
            <div v-if="faceDetected && cameraEnabled" class="absolute top-4 right-4 bg-green-500 px-3 py-1 rounded-full text-white text-sm font-semibold">
              ✓ Face Detected
            </div>
          </div>
          <button
            v-if="!cameraEnabled"
            @click="enableCamera"
            class="w-full mt-4 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-semibold"
          >
            📹 Enable Camera
          </button>
        </div>

        <!-- Screen Share Preview -->
        <div class="mb-8">
          <div class="flex items-center justify-between mb-3">
            <h4 class="font-semibold text-gray-900">🖥️ Screen Share</h4>
            <span
              class="px-3 py-1 rounded-full text-sm font-semibold"
              :class="screenShareEnabled ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
            >
              {{ screenShareEnabled ? '✓ Active' : '✗ Inactive' }}
            </span>
          </div>
          <div class="relative bg-black rounded-xl overflow-hidden" style="aspect-ratio: 16/9">
            <video
              ref="screenVideo"
              autoplay
              muted
              playsinline
              class="w-full h-full object-contain"
            ></video>
            <div v-if="!screenShareEnabled" class="absolute inset-0 flex items-center justify-center bg-gray-800">
              <div class="text-center text-white">
                <p class="text-xl mb-2">Screen share not enabled</p>
                <p class="text-sm text-gray-400">Click button below to share screen</p>
              </div>
            </div>
          </div>
          <button
            v-if="!screenShareEnabled"
            @click="enableScreenShare"
            class="w-full mt-4 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-semibold"
          >
            🖥️ Share Screen
          </button>
        </div>

        <!-- Proctoring Rules -->
        <div class="bg-yellow-50 border-2 border-yellow-300 rounded-xl p-6 mb-6">
          <h4 class="font-bold text-gray-900 mb-3">⚠️ Proctoring Rules</h4>
          <ul class="space-y-2 text-sm text-gray-700">
            <li v-if="testInfo.require_webcam">✓ Camera must remain on throughout the test</li>
            <li>✓ Screen sharing must remain active</li>
            <li v-if="testInfo.detect_multiple_faces">✓ Only one person should be visible</li>
            <li v-if="!testInfo.allow_tab_switch">✓ Do not switch tabs or windows</li>
            <li>✓ Do not use external resources unless permitted</li>
            <li>✓ Your teacher can monitor your screen and camera in real-time</li>
          </ul>
        </div>

        <!-- Start Test Button -->
        <button
          @click="startTest"
          :disabled="!canStartTest"
          class="w-full px-6 py-4 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-semibold text-lg"
        >
          <span v-if="!cameraEnabled || !screenShareEnabled">
            {{ !cameraEnabled ? 'Enable Camera First' : 'Enable Screen Share First' }}
          </span>
          <span v-else>🚀 Start Test</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'
import { useToast } from 'vue-toastification'
import { FaceDetector, FilesetResolver } from '@mediapipe/tasks-vision'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const step = ref(1)
const loading = ref(false)
const testCode = ref(['', '', '', ''])
const codeInputs = ref([])
const testInfo = ref(null)

const cameraEnabled = ref(false)
const screenShareEnabled = ref(false)
const cameraVideo = ref(null)
const screenVideo = ref(null)
const cameraStream = ref(null)
const screenStream = ref(null)
const faceDetected = ref(false)
const faceDetector = ref(null)

const canStartTest = computed(() => {
  // Allow starting if camera and screen share are enabled
  // Face detection is optional (will be verified during test)
  return cameraEnabled.value && screenShareEnabled.value
})

const handleCodeInput = (index, event) => {
  const value = event.target.value
  if (value && index < 3) {
    codeInputs.value[index + 1]?.focus()
  }
}

const handleKeyDown = (index, event) => {
  if (event.key === 'Backspace' && !testCode.value[index] && index > 0) {
    codeInputs.value[index - 1]?.focus()
  }
}

const validateCode = async () => {
  const code = testCode.value.join('')
  if (code.length !== 4) return

  loading.value = true
  try {
    const response = await api.get(`/tests/validate-code/${code}`)
    testInfo.value = response.data.test
    step.value = 2
    toast.success('Test found! Setup monitoring to continue')
  } catch (error) {
    console.error('Invalid code:', error)
    toast.error('Invalid test code. Please check and try again.')
    testCode.value = ['', '', '', '']
    codeInputs.value[0]?.focus()
  } finally {
    loading.value = false
  }
}

const enableCamera = async () => {
  try {
    // Check if mediaDevices API is available
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('Camera API not supported. Please use HTTPS or a modern browser.')
    }
    
    const stream = await navigator.mediaDevices.getUserMedia({ 
      video: { 
        width: { ideal: 1280 },
        height: { ideal: 720 },
        facingMode: 'user'
      }, 
      audio: true 
    })
    cameraStream.value = stream
    if (cameraVideo.value) {
      cameraVideo.value.srcObject = stream
    }
    cameraEnabled.value = true
    toast.success('Camera enabled')
    
    // Initialize face detection
    await initFaceDetection()
  } catch (error) {
    console.error('Camera error:', error)
    if (error.name === 'NotAllowedError') {
      toast.error('Camera permission denied. Please allow camera access.')
    } else if (error.name === 'NotFoundError') {
      toast.error('No camera found on this device.')
    } else if (error.message.includes('not supported')) {
      toast.error('Camera requires HTTPS. Please check your connection.')
    } else {
      toast.error('Failed to enable camera. Please check permissions.')
    }
  }
}

const enableScreenShare = async () => {
  try {
    // Check if mediaDevices API is available
    if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
      throw new Error('Screen sharing API not supported. Please use HTTPS or a modern browser.')
    }
    
    const stream = await navigator.mediaDevices.getDisplayMedia({ 
      video: { 
        cursor: 'always',
        displaySurface: 'monitor'
      },
      audio: false 
    })
    screenStream.value = stream
    if (screenVideo.value) {
      screenVideo.value.srcObject = stream
    }
    screenShareEnabled.value = true
    toast.success('Screen sharing enabled')
    
    // Handle user stopping screen share
    stream.getVideoTracks()[0].addEventListener('ended', () => {
      screenShareEnabled.value = false
      toast.warning('Screen sharing stopped!')
    })
  } catch (error) {
    console.error('Screen share error:', error)
    if (error.name === 'NotAllowedError') {
      toast.error('Screen sharing permission denied.')
    } else if (error.name === 'NotFoundError') {
      toast.error('No screen available to share.')
    } else if (error.message.includes('not supported')) {
      toast.error('Screen sharing requires HTTPS. Please check your connection.')
    } else {
      toast.error('Failed to enable screen sharing')
    }
  }
}

const initFaceDetection = async () => {
  try {
    const vision = await FilesetResolver.forVisionTasks(
      "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm"
    )
    
    faceDetector.value = await FaceDetector.createFromOptions(vision, {
      baseOptions: {
        modelAssetPath: "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite",
        delegate: "GPU"
      },
      runningMode: "VIDEO"
    })
    
    // Wait for video to be fully ready
    if (cameraVideo.value) {
      if (cameraVideo.value.readyState < 2) {
        await new Promise(resolve => {
          cameraVideo.value.addEventListener('loadeddata', resolve, { once: true })
        })
      }
      // Additional buffer to ensure video is playing
      await new Promise(resolve => setTimeout(resolve, 1000))
    }
    
    // Start face detection loop
    detectFaces()
  } catch (error) {
    console.error('Face detection init error:', error)
    toast.warning('Face detection unavailable')
  }
}

const detectFaces = () => {
  if (!faceDetector.value || !cameraVideo.value || !cameraEnabled.value) return
  
  let lastDetectionTime = 0
  const detectionInterval = 500 // Check every 500ms
  
  const detect = () => {
    try {
      const now = performance.now()
      
      // Only detect if video is ready and enough time has passed
      if (cameraVideo.value && 
          cameraVideo.value.readyState === 4 && 
          !cameraVideo.value.paused &&
          now - lastDetectionTime >= detectionInterval) {
        
        const detections = faceDetector.value.detectForVideo(cameraVideo.value, now)
        faceDetected.value = detections.detections.length > 0
        lastDetectionTime = now
      }
    } catch (error) {
      // Only log real errors, not timing issues
      if (!error.message.includes('video mode') && !error.message.includes('runningMode')) {
        console.debug('Detection frame skipped:', error.message)
      }
    }
    
    if (cameraEnabled.value) {
      requestAnimationFrame(detect)
    }
  }
  
  detect()
}

const startTest = async () => {
  if (!canStartTest.value) return
  
  try {
    const response = await api.post('/tests/start-attempt', {
      test_code: testCode.value.join('')
    })
    
    // Check admission mode
    const admissionMode = response.data.admission_mode || 'auto_admit'
    
    // Store streams for test interface
    sessionStorage.setItem('cameraStream', 'active')
    sessionStorage.setItem('screenStream', 'active')
    sessionStorage.setItem('attemptId', response.data.id)
    
    // If manual approval required, redirect to waiting room
    if (admissionMode === 'manual_approval') {
      console.log('📋 Manual approval required - redirecting to waiting room')
      router.push({
        path: '/waiting-room',
        query: {
          testId: response.data.test_id,
          attemptId: response.data.id,
          testCode: testCode.value.join(''),
          reasons: 'Waiting for teacher approval to start test',
          pausedBy: 'system'
        }
      })
    } else {
      // Auto admit - go directly to test
      router.push(`/test/${response.data.test_id}`)
    }
  } catch (error) {
    console.error('Failed to start test:', error)
    toast.error(error.response?.data?.detail || 'Failed to start test')
  }
}

onMounted(() => {
  // Focus first input
  if (codeInputs.value[0]) {
    codeInputs.value[0].focus()
  }
})

onUnmounted(() => {
  // Cleanup streams
  if (cameraStream.value) {
    cameraStream.value.getTracks().forEach(track => track.stop())
  }
  if (screenStream.value) {
    screenStream.value.getTracks().forEach(track => track.stop())
  }
})
</script>
