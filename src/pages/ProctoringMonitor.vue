<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white">
    <header class="bg-gray-900 shadow-lg border-b border-gray-700">
      <div class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold">Live Proctoring Monitor</h1>
          <p class="text-sm text-gray-400">Test: {{ test?.title }} ({{ test?.test_code }})</p>
        </div>
        <div class="flex items-center gap-4">
          <div class="text-center bg-gray-800 px-4 py-2 rounded-lg">
            <p class="text-xs text-gray-400">Active Students</p>
            <p class="text-2xl font-bold text-green-400">{{ activeStudents.length }}</p>
          </div>
          <div class="text-center bg-gray-800 px-4 py-2 rounded-lg">
            <p class="text-xs text-gray-400">Total Violations</p>
            <p class="text-2xl font-bold text-red-400">{{ totalViolations }}</p>
          </div>
          <button @click="goBack" class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg font-semibold">
            ← Back
          </button>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-6 py-8">
      <div v-if="activeStudents.length === 0" class="text-center py-20">
        <p class="text-xl text-gray-400 mb-4">Waiting for students to join...</p>
        <div class="animate-pulse text-4xl">⏳</div>
      </div>

      <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2">
          <h2 class="text-xl font-bold mb-4">Student Feeds</h2>
          <div class="grid grid-cols-1 gap-6">
            <div v-for="student in activeStudents" :key="student.sid" 
              class="bg-gray-800 rounded-xl overflow-hidden shadow-lg border-2"
              :class="student.violations > 3 ? 'border-red-500' : student.violations > 0 ? 'border-yellow-500' : 'border-gray-700'">
              
              <!-- Student Header -->
              <div class="p-4 bg-gray-900 border-b border-gray-700 flex justify-between items-center">
                <div>
                  <h3 class="font-bold text-lg">{{ student.student_name }}</h3>
                  <p class="text-sm text-gray-400">Student ID: {{ student.student_id }}</p>
                </div>
                <div class="flex items-center gap-2">
                  <span v-if="student.audioLevel > 10" class="flex items-center gap-1 bg-green-500 px-2 py-1 rounded text-xs">
                    🎤 {{ student.audioLevel }}
                  </span>
                  <span class="px-3 py-1 rounded text-xs font-bold"
                    :class="student.violations > 3 ? 'bg-red-500' : student.violations > 0 ? 'bg-yellow-500' : 'bg-green-500'">
                    {{ student.violations > 0 ? `⚠️ ${student.violations} Violations` : '✓ Clean' }}
                  </span>
                </div>
              </div>

              <!-- Dual Feed: Camera + Screen -->
              <div class="grid grid-cols-2 gap-2 p-2">
                <!-- Camera Feed -->
                <div class="relative">
                  <div class="aspect-video bg-black rounded-lg overflow-hidden relative">
                    <video v-if="student.cameraStream" 
                      :ref="el => setupVideoElement(el, student.sid, 'camera')"
                      autoplay 
                      playsinline
                      muted
                      class="w-full h-full object-cover">
                    </video>
                    <img v-else-if="student.lastCameraFrame" 
                      :src="student.lastCameraFrame" 
                      class="w-full h-full object-cover" />
                    <div v-else class="w-full h-full flex items-center justify-center text-gray-500">
                      <div class="text-center">
                        <span class="text-4xl">📷</span>
                        <p class="text-sm mt-2">No Camera</p>
                      </div>
                    </div>
                    <div class="absolute bottom-2 left-2 bg-black bg-opacity-70 px-2 py-1 rounded text-xs">
                      📷 Camera Feed
                    </div>
                  </div>
                </div>

                <!-- Screen Feed -->
                <div class="relative">
                  <div class="aspect-video bg-black rounded-lg overflow-hidden relative">
                    <video v-if="student.screenStream" 
                      :ref="el => setupVideoElement(el, student.sid, 'screen')"
                      autoplay 
                      playsinline
                      muted
                      class="w-full h-full object-contain">
                    </video>
                    <img v-else-if="student.lastScreenFrame" 
                      :src="student.lastScreenFrame" 
                      class="w-full h-full object-contain" />
                    <div v-else class="w-full h-full flex items-center justify-center text-gray-500">
                      <div class="text-center">
                        <span class="text-4xl">🖥️</span>
                        <p class="text-sm mt-2">No Screen Share</p>
                      </div>
                    </div>
                    <div class="absolute bottom-2 left-2 bg-black bg-opacity-70 px-2 py-1 rounded text-xs">
                      🖥️ Screen Share
                    </div>
                  </div>
                </div>
              </div>

              <!-- Student Stats -->
              <div class="px-4 pb-2 grid grid-cols-3 gap-2 text-sm">
                <div class="text-center bg-gray-900 py-2 rounded">
                  <p class="text-xs text-gray-400">Status</p>
                  <p class="font-bold text-green-400">Active</p>
                </div>
                <div class="text-center bg-gray-900 py-2 rounded">
                  <p class="text-xs text-gray-400">Face Count</p>
                  <p class="font-bold">{{ student.faceCount || 1 }}</p>
                </div>
                <div class="text-center bg-gray-900 py-2 rounded">
                  <p class="text-xs text-gray-400">Tab Switches</p>
                  <p class="font-bold text-orange-400">{{ student.tabSwitches || 0 }}</p>
                </div>
              </div>
              
              <!-- Teacher Actions -->
              <div class="px-4 pb-4 flex gap-2">
                <button 
                  @click="sendToWaitingRoom(student)"
                  class="flex-1 px-3 py-2 bg-yellow-600 hover:bg-yellow-700 rounded-lg text-sm font-semibold transition-colors">
                  ⏸️ Pause Student
                </button>
                <button 
                  @click="terminateStudent(student)"
                  class="flex-1 px-3 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-sm font-semibold transition-colors">
                  ❌ Terminate
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="space-y-4">
          <!-- Waiting Room Students -->
          <div v-if="waitingRoomStudents.length > 0" class="bg-yellow-900 bg-opacity-30 border-2 border-yellow-600 rounded-xl p-4 shadow-lg">
            <h3 class="font-bold mb-4 flex items-center gap-2">
              <span class="text-yellow-400">⏸️</span> Waiting Room ({{ waitingRoomStudents.length }})
            </h3>
            <div class="space-y-3">
              <div v-for="student in waitingRoomStudents" :key="student.sid" class="bg-gray-800 rounded-lg p-3">
                <div class="flex justify-between items-start mb-2">
                  <div>
                    <p class="font-semibold flex items-center gap-2">
                      {{ student.name }}
                      <span v-if="student.isInitialEntry" class="text-xs px-2 py-0.5 bg-blue-600 rounded-full">NEW</span>
                    </p>
                    <p class="text-xs text-gray-400">Waiting: {{ student.waitingTime }}</p>
                  </div>
                </div>
                <div class="mb-3">
                  <p v-if="student.isInitialEntry" class="text-xs text-blue-200">
                    👋 Waiting for approval to start test
                  </p>
                  <p v-else class="text-xs text-yellow-200">
                    🚨 {{ student.reason }}
                  </p>
                </div>
                <div class="flex gap-2">
                  <button 
                    @click="approveStudent(student)"
                    class="flex-1 px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm font-semibold">
                    ✓ {{ student.isInitialEntry ? 'Start Test' : 'Resume' }}
                  </button>
                  <button 
                    @click="terminateFromWaiting(student)"
                    class="flex-1 px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm font-semibold">
                    ✗ Terminate
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <div class="bg-gray-800 rounded-xl p-4 shadow-lg">
            <h3 class="font-bold mb-4 flex items-center gap-2">
              <span class="text-red-500">🚨</span> Live Alerts
            </h3>
            <div class="space-y-2 max-h-96 overflow-y-auto">
              <div v-for="(alert, idx) in recentAlerts" :key="idx" 
                class="p-3 rounded-lg text-sm"
                :class="alert.severity === 'critical' ? 'bg-red-900 bg-opacity-50' : alert.severity === 'high' ? 'bg-orange-900 bg-opacity-50' : 'bg-yellow-900 bg-opacity-50'">
                <div class="flex justify-between items-start mb-1">
                  <span class="font-semibold text-white">{{ alert.student_name }}</span>
                  <span class="text-xs text-gray-400">{{ formatTime(alert.timestamp) }}</span>
                </div>
                <p class="text-gray-300">{{ alert.details }}</p>
              </div>
              <div v-if="recentAlerts.length === 0" class="text-center py-8 text-gray-500">
                No violations detected
              </div>
            </div>
          </div>

          <div class="bg-gray-800 rounded-xl p-4 shadow-lg">
            <h3 class="font-bold mb-4">Violation Summary</h3>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between items-center">
                <span class="text-gray-400">No Face Detected</span>
                <span class="font-bold text-red-400">{{ violationTypes.no_face_detected || 0 }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-gray-400">Multiple Faces</span>
                <span class="font-bold text-red-400">{{ violationTypes.multiple_faces || 0 }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-gray-400">Tab Switches</span>
                <span class="font-bold text-orange-400">{{ violationTypes.tab_switch || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { io } from 'socket.io-client'
import api from '../api'

const route = useRoute()
const router = useRouter()

const test = ref(null)
const students = ref({})
const recentAlerts = ref([])
const socket = ref(null)
const peerConnections = ref({})
const waitingRoomStudents = ref([])
const videoElements = ref({}) // Store video element references

const activeStudents = computed(() => Object.values(students.value))
const totalViolations = computed(() => 
  activeStudents.value.reduce((sum, s) => sum + (s.violations || 0), 0)
)

const violationTypes = computed(() => {
  const types = {}
  recentAlerts.value.forEach(alert => {
    types[alert.type] = (types[alert.type] || 0) + 1
  })
  return types
})

const setupVideoElement = (el, studentId, type) => {
  if (!el) return
  
  // Store element reference
  const key = `${studentId}-${type}`
  videoElements.value[key] = el
  
  const student = students.value[studentId]
  if (!student) return

  if (type === 'camera' && student.cameraStream) {
    el.srcObject = student.cameraStream
    el.play().catch(e => console.error('Error playing camera:', e))
    console.log(`✅ Set camera stream for ${studentId}`)
  } else if (type === 'screen' && student.screenStream) {
    el.srcObject = student.screenStream
    el.play().catch(e => console.error('Error playing screen:', e))
    console.log(`✅ Set screen stream for ${studentId}`)
  }
}

// Watch for stream changes and update video elements
watch(() => students.value, (newStudents) => {
  Object.entries(newStudents).forEach(([sid, student]) => {
    if (student.cameraStream) {
      const cameraEl = videoElements.value[`${sid}-camera`]
      if (cameraEl && cameraEl.srcObject !== student.cameraStream) {
        cameraEl.srcObject = student.cameraStream
        cameraEl.play().catch(e => console.error('Error playing camera:', e))
        console.log(`🔄 Updated camera stream for ${sid}`)
      }
    }
    if (student.screenStream) {
      const screenEl = videoElements.value[`${sid}-screen`]
      if (screenEl && screenEl.srcObject !== student.screenStream) {
        screenEl.srcObject = student.screenStream
        screenEl.play().catch(e => console.error('Error playing screen:', e))
        console.log(`🔄 Updated screen stream for ${sid}`)
      }
    }
  })
}, { deep: true })

const formatTime = (timestamp) => {
  const now = Date.now()
  const diff = now - new Date(timestamp).getTime()
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  
  if (minutes === 0) return `${seconds}s ago`
  if (minutes < 60) return `${minutes}m ago`
  return `${Math.floor(minutes / 60)}h ago`
}

const loadTest = async () => {
  try {
    const testId = route.params.testId
    const response = await api.get(`/tests/${testId}`)
    test.value = response.data
  } catch (error) {
    console.error('Failed to load test:', error)
  }
}

const initializeSocket = () => {
  socket.value = io('http://localhost:8000', {
    transports: ['websocket']
  })

  socket.value.on('connect', () => {
    socket.value.emit('join_test_as_teacher', {
      test_code: test.value.test_code
    })
  })

  socket.value.on('monitoring_started', (data) => {
    data.students.forEach(student => {
      students.value[student.sid] = {
        ...student,
        violations: 0,
        audioLevel: 0,
        lastFrame: null
      }
    })
  })

  socket.value.on('student_joined', (data) => {
    console.log('✅ Student joined:', data)
    students.value[data.sid] = {
      sid: data.sid,
      student_id: data.student_id,
      student_name: data.student_name,
      attempt_id: data.attempt_id,
      violations: 0,
      audioLevel: 0,
      faceCount: 1,
      tabSwitches: 0,
      lastCameraFrame: null,
      lastScreenFrame: null,
      cameraStream: null,
      screenStream: null,
      cameraPeerConnection: null,
      screenPeerConnection: null
    }
  })

  socket.value.on('student_left', (data) => {
    console.log('👋 Student left:', data)
    const student = students.value[data.student_id]
    
    // Clean up peer connections
    if (student) {
      if (student.cameraPeerConnection) {
        student.cameraPeerConnection.close()
      }
      if (student.screenPeerConnection) {
        student.screenPeerConnection.close()
      }
    }
    
    delete students.value[data.student_id]
  })

  socket.value.on('student_audio_level', (data) => {
    if (students.value[data.sid]) {
      students.value[data.sid].audioLevel = data.level
    }
  })

  socket.value.on('face_detection_update', (data) => {
    if (students.value[data.sid]) {
      students.value[data.sid].faceCount = data.face_count
    }
  })

  socket.value.on('student_violation', (data) => {
    if (students.value[data.sid]) {
      students.value[data.sid].violations++
      
      if (data.violation.type === 'tab_switch') {
        students.value[data.sid].tabSwitches = (students.value[data.sid].tabSwitches || 0) + 1
      }
    }

    recentAlerts.value.unshift({
      student_name: data.student_name,
      type: data.violation.type,
      severity: data.violation.severity,
      details: data.violation.details,
      timestamp: data.violation.timestamp
    })

    if (recentAlerts.value.length > 50) {
      recentAlerts.value.pop()
    }
  })
  
  socket.value.on('student_in_waiting_room', (data) => {
    // Add student to waiting room
    const isInitialEntry = data.reason && data.reason.includes('approval')
    
    waitingRoomStudents.value.push({
      sid: data.sid,
      name: data.name,
      user_id: data.user_id,
      test_id: data.test_id,
      attempt_id: data.attempt_id,
      reason: data.reason || 'Flagged for suspicious activity',
      isInitialEntry: isInitialEntry,
      waitingTime: '0:00'
    })
    
    // Only remove from active students if not initial entry
    if (!isInitialEntry) {
      delete students.value[data.sid]
    }
  })
  
  socket.value.on('student_flagged', (data) => {
    console.log('Student flagged by ML:', data)
    recentAlerts.value.unshift({
      student_name: data.student_name,
      type: 'ml_flagged',
      severity: 'critical',
      details: `ML System Flagged: ${data.details}`,
      timestamp: new Date().toISOString()
    })
  })

  // WebRTC offer handler - receives offer from student
  socket.value.on('webrtc_offer', async (data) => {
    console.log(`📥 Received WebRTC offer from ${data.student_name} for ${data.stream_type}`)
    
    try {
      const student = students.value[data.sid]
      if (!student) {
        console.warn('Student not found for WebRTC offer')
        return
      }

      // Create peer connection
      const pc = new RTCPeerConnection({
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' },
          { urls: 'stun:stun1.l.google.com:19302' }
        ]
      })

      // Store peer connection
      const pcKey = data.stream_type === 'camera' ? 'cameraPeerConnection' : 'screenPeerConnection'
      student[pcKey] = pc

      // Handle incoming tracks
      pc.ontrack = (event) => {
        console.log(`📹 Received ${event.track.kind} track from ${data.student_name} for ${data.stream_type}`)
        
        if (data.stream_type === 'camera') {
          student.cameraStream = event.streams[0]
          console.log('✅ Camera stream assigned to student')
        } else {
          student.screenStream = event.streams[0]
          console.log('✅ Screen stream assigned to student')
        }
        
        // Force Vue reactivity update
        students.value = { ...students.value }
      }

      // Handle DataChannel for audio levels (camera stream only)
      if (data.stream_type === 'camera') {
        pc.ondatachannel = (event) => {
          const dataChannel = event.channel
          console.log('📡 DataChannel opened:', dataChannel.label)
          
          dataChannel.onmessage = (e) => {
            try {
              const audioData = JSON.parse(e.data)
              if (student) {
                student.audioLevel = audioData.level
              }
            } catch (error) {
              console.error('Error parsing audio level:', error)
            }
          }
        }
      }

      // Handle ICE candidates
      pc.onicecandidate = (event) => {
        if (event.candidate && socket.value?.connected) {
          socket.value.emit('webrtc_ice_candidate', {
            candidate: event.candidate,
            stream_type: data.stream_type,
            student_sid: data.sid
          })
          console.log(`📤 Sent ICE candidate for ${data.stream_type}`)
        }
      }
      
      // Monitor connection state
      pc.onconnectionstatechange = () => {
        console.log(`🔌 ${data.stream_type} connection state:`, pc.connectionState)
      }
      
      pc.oniceconnectionstatechange = () => {
        console.log(`🧊 ${data.stream_type} ICE connection state:`, pc.iceConnectionState)
      }

      // Set remote description and create answer
      await pc.setRemoteDescription(new RTCSessionDescription(data.offer))
      const answer = await pc.createAnswer()
      await pc.setLocalDescription(answer)

      // Send answer back to student
      socket.value.emit('webrtc_answer', {
        answer: answer,
        stream_type: data.stream_type,
        student_sid: data.sid
      })
      console.log(`📤 Sent WebRTC answer for ${data.stream_type}`)
      
    } catch (error) {
      console.error('Error handling WebRTC offer:', error)
    }
  })

  // Handle ICE candidates from student
  socket.value.on('webrtc_ice_candidate', async (data) => {
    console.log(`📥 Received ICE candidate for ${data.stream_type}`)
    
    const student = students.value[data.sid]
    if (!student) return

    const pcKey = data.stream_type === 'camera' ? 'cameraPeerConnection' : 'screenPeerConnection'
    const pc = student[pcKey]
    
    if (pc && data.candidate) {
      try {
        await pc.addIceCandidate(new RTCIceCandidate(data.candidate))
      } catch (error) {
        console.error('Error adding ICE candidate:', error)
      }
    }
  })
}

const sendToWaitingRoom = (student) => {
  if (!confirm(`Send ${student.student_name} to waiting room?`)) return
  
  if (socket.value?.connected) {
    socket.value.emit('teacher_pause_student', {
      sid: student.sid,
      student_id: student.student_id,
      test_id: test.value.id,
      reason: 'Paused by teacher for manual review'
    })
  }
}

const terminateStudent = (student) => {
  if (!confirm(`Terminate test for ${student.student_name}? This action cannot be undone.`)) return
  
  if (socket.value?.connected) {
    socket.value.emit('teacher_terminate_student', {
      sid: student.sid,
      student_id: student.student_id,
      test_id: test.value.id
    })
    
    delete students.value[student.sid]
  }
}

const approveStudent = (student) => {
  if (socket.value?.connected) {
    socket.value.emit('approve_student', {
      sid: student.sid,
      student_id: student.user_id,
      test_id: student.test_id
    })
    
    // Remove from waiting room
    waitingRoomStudents.value = waitingRoomStudents.value.filter(s => s.sid !== student.sid)
  }
}

const terminateFromWaiting = (student) => {
  if (!confirm(`Terminate test for ${student.name}?`)) return
  
  if (socket.value?.connected) {
    socket.value.emit('terminate_from_waiting', {
      sid: student.sid,
      student_id: student.user_id,
      test_id: student.test_id
    })
    
    // Remove from waiting room
    waitingRoomStudents.value = waitingRoomStudents.value.filter(s => s.sid !== student.sid)
  }
}

const goBack = () => {
  router.push('/teacher/dashboard')
}

onMounted(async () => {
  await loadTest()
  initializeSocket()
})

onUnmounted(() => {
  if (socket.value) {
    socket.value.disconnect()
  }
})
</script>
