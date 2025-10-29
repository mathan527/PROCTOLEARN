import { ref, onMounted, onUnmounted } from 'vue'
import { FaceDetector, FilesetResolver } from '@mediapipe/tasks-vision'
import * as tf from '@tensorflow/tfjs'
import * as blazeface from '@tensorflow-models/blazeface'
import * as faceLandmarksDetection from '@tensorflow-models/face-landmarks-detection'
import * as cocoSsd from '@tensorflow-models/coco-ssd'

export function useProctoring(onViolation) {
  const videoRef = ref(null)
  const stream = ref(null)
  
  // MediaPipe face detector
  const faceDetector = ref(null)
  
  // TensorFlow models
  const blazefaceModel = ref(null)
  const faceLandmarksModel = ref(null)
  const objectDetectionModel = ref(null)
  
  const detectionInterval = ref(null)
  const audioContext = ref(null)
  const audioAnalyser = ref(null)
  const audioLevel = ref(0)
  const tabSwitchCount = ref(0)
  const lastFacePosition = ref(null)
  const lastHeadPose = ref({ pitch: 0, yaw: 0, roll: 0 })
  const consecutiveNoFace = ref(0)
  const consecutiveLookingAway = ref(0)
  const isFullscreen = ref(false)
  const isMobile = ref(false)
  const suspiciousObjects = ref([])
  const eyeClosedCount = ref(0)
  const windowMinimized = ref(false)
  const browserOutOfFocus = ref(false)
  
  // Face detection status for UI visualization
  const faceDetectionStatus = ref({
    faceDetected: false,
    eyesOpen: true,
    lookingAtScreen: true,
    faceBoundingBox: null // {x, y, width, height}
  })
  
  // Violation tracking for waiting room
  const violationScore = ref(0)
  const severeViolations = ref([])
  const WAITING_ROOM_THRESHOLD = 10 // Send to waiting room at this score

  let visibilityChangeHandler
  let fullscreenChangeHandler
  let keyboardHandler
  let mouseLeaveHandler
  let contextMenuHandler
  let blurHandler
  let blurTimeout = null
  let lastBlurTime = 0

  const detectMobile = () => {
    const ua = navigator.userAgent
    isMobile.value = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua) ||
                     ('ontouchstart' in window) ||
                     (navigator.maxTouchPoints > 0)
    return isMobile.value
  }

  // Enhanced violation tracking with severity scoring
  const trackViolation = (violation) => {
    // Assign severity scores
    const severityScores = {
      no_face_detected: 15,
      multiple_faces: 10,
      looking_away: 3,
      eyes_closed: 4,
      excessive_movement: 4,
      suspicious_object: 15, // High penalty for phones, books, etc
      tab_switch: 10,
      mouse_left: 5,
      window_lost_focus: 8, // Increased from 2
      fullscreen_exit: 20, // CRITICAL - trying to exit fullscreen
      window_minimized: 20, // CRITICAL - minimizing browser
      blocked_key: 3,
      right_click: 2
    }

    const score = severityScores[violation.type] || 1
    violationScore.value += score

    // Track severe violations
    if (score >= 5) {
      severeViolations.value.push({
        type: violation.type,
        details: violation.details,
        timestamp: new Date().toISOString(),
        score: score
      })
    }

    console.log(`🚨 Violation: ${violation.type} (+${score} points) | Total: ${violationScore.value}`)

    // Send to waiting room if threshold exceeded
    if (violationScore.value >= WAITING_ROOM_THRESHOLD) {
      const reasons = severeViolations.value.map(v => 
        `${v.type.replace(/_/g, ' ').toUpperCase()}: ${v.details}`
      )
      
      onViolation({
        type: 'severe_violations_threshold',
        severity: 'critical',
        details: `Multiple violations detected (Score: ${violationScore.value})`,
        action: 'waiting_room',
        reasons: reasons
      })
    } else {
      // Normal violation callback
      onViolation(violation)
    }
  }

  // Model initialization status tracking
  const modelStatus = ref({
    mediapipe: { loaded: false, retries: 0, maxRetries: 3 },
    blazeface: { loaded: false, retries: 0, maxRetries: 3 },
    facelandmarks: { loaded: false, retries: 0, maxRetries: 3 },
    objectdetection: { loaded: false, retries: 0, maxRetries: 3 }
  })

  const detectionMode = ref('full') // 'full', 'basic', or 'manual'

  // Retry mechanism for failed models
  const retryModelInitialization = async (modelName, initFunction) => {
    const status = modelStatus.value[modelName]
    
    if (status.loaded || status.retries >= status.maxRetries) {
      return false
    }

    console.log(`🔄 Retrying ${modelName} initialization (Attempt ${status.retries + 1}/${status.maxRetries})`)
    status.retries++

    try {
      await initFunction()
      status.loaded = true
      console.log(`✅ ${modelName} initialized successfully on retry`)
      return true
    } catch (error) {
      console.warn(`❌ ${modelName} retry ${status.retries} failed:`, error.message)
      
      if (status.retries >= status.maxRetries) {
        console.error(`❌ ${modelName} failed after ${status.maxRetries} attempts. Switching to fallback mode.`)
        adjustDetectionMode()
      }
      return false
    }
  }

  // Adjust detection mode based on available models
  const adjustDetectionMode = () => {
    const loadedCount = Object.values(modelStatus.value).filter(s => s.loaded).length
    
    if (loadedCount >= 3) {
      detectionMode.value = 'full'
      console.log('🎯 Detection Mode: FULL - All ML models active')
    } else if (loadedCount >= 1) {
      detectionMode.value = 'basic'
      console.log('⚠️ Detection Mode: BASIC - Limited ML detection active')
    } else {
      detectionMode.value = 'manual'
      console.log('⚠️ Detection Mode: MANUAL - Only tab/window monitoring active')
    }
  }

  // Fallback detection using basic video analysis (no ML)
  const fallbackFaceDetection = () => {
    if (!videoRef.value) return false

    try {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      canvas.width = videoRef.value.videoWidth
      canvas.height = videoRef.value.videoHeight
      
      ctx.drawImage(videoRef.value, 0, 0, canvas.width, canvas.height)
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
      
      // Simple brightness check - if video is too dark, no face likely present
      let totalBrightness = 0
      for (let i = 0; i < imageData.data.length; i += 4) {
        const r = imageData.data[i]
        const g = imageData.data[i + 1]
        const b = imageData.data[i + 2]
        totalBrightness += (r + g + b) / 3
      }
      
      const avgBrightness = totalBrightness / (imageData.data.length / 4)
      
      // If too dark (< 20) or too bright (> 250), suspicious
      return avgBrightness > 20 && avgBrightness < 250
    } catch (error) {
      console.debug('Fallback detection error:', error.message)
      return true // Assume face present to avoid false positives
    }
  }

  const initializeCamera = async () => {
    try {
      console.log('📷 Requesting camera access...')
      
      // Show notification that monitoring is starting
      if (typeof window !== 'undefined' && window.showMonitoringNotification) {
        window.showMonitoringNotification('AI Monitoring Initializing...', 'info')
      }
      
      detectMobile()
      
      const constraints = isMobile.value ? {
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        },
        audio: false
      } : {
        video: { 
          width: 640, 
          height: 480,
          facingMode: 'user'
        },
        audio: true
      }
      
      stream.value = await navigator.mediaDevices.getUserMedia(constraints)

      console.log('✅ Camera access granted')
      
      if (typeof window !== 'undefined' && window.showMonitoringNotification) {
        window.showMonitoringNotification('Camera Connected ✓', 'success')
      }

      if (videoRef.value) {
        videoRef.value.srcObject = stream.value
        videoRef.value.setAttribute('playsinline', 'true')
        videoRef.value.setAttribute('webkit-playsinline', 'true')
        
        await new Promise((resolve) => {
          videoRef.value.onloadedmetadata = () => {
            videoRef.value.play().then(() => {
              console.log('▶️ Video playing')
              resolve()
            })
          }
        })
      }

      if (!isMobile.value) {
        await initializeAudioMonitoring()
      }
      
      // Notify AI model loading
      if (typeof window !== 'undefined' && window.showMonitoringNotification) {
        window.showMonitoringNotification('Loading AI Detection Models...', 'info')
      }
      
      await initializeFaceDetection()
      await initializeBlazeFaceModel()
      await initializeFaceLandmarksModel()
      await initializeObjectDetection()
      initializeTabSwitchDetection()
      
      if (!isMobile.value) {
        initializeFullscreenMonitoring()
        initializeKeyboardBlocking()
        initializeMouseMonitoring()
      }
      
      // Final success notification
      if (typeof window !== 'undefined' && window.showMonitoringNotification) {
        window.showMonitoringNotification('AI Monitoring Active 🛡️', 'success')
      }
      
      return true
    } catch (error) {
      console.error('❌ Camera access denied:', error)
      
      if (typeof window !== 'undefined' && window.showMonitoringNotification) {
        window.showMonitoringNotification('Camera Access Denied!', 'error')
      }
      
      return false
    }
  }

  const initializeAudioMonitoring = async () => {
    try {
      audioContext.value = new AudioContext()
      const source = audioContext.value.createMediaStreamSource(stream.value)
      audioAnalyser.value = audioContext.value.createAnalyser()
      audioAnalyser.value.fftSize = 256
      source.connect(audioAnalyser.value)

      const dataArray = new Uint8Array(audioAnalyser.value.frequencyBinCount)
      
      const checkAudioLevel = () => {
        audioAnalyser.value.getByteFrequencyData(dataArray)
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length
        audioLevel.value = Math.round(average)
      }

      setInterval(checkAudioLevel, 100)
    } catch (error) {
      console.error('Audio monitoring failed:', error)
    }
  }

  const initializeTabSwitchDetection = () => {
    visibilityChangeHandler = () => {
      if (document.hidden) {
        tabSwitchCount.value++
        trackViolation({
          type: 'tab_switch',
          severity: 'critical',
          details: `Student switched tabs (Total: ${tabSwitchCount.value})`
        })
      }
    }

    blurHandler = () => {
      // Clear any existing timeout
      if (blurTimeout) {
        clearTimeout(blurTimeout)
      }
      
      // Prevent duplicate violations within 10 seconds
      const now = Date.now()
      if (now - lastBlurTime < 10000) {
        console.log('⏭️ Skipping duplicate blur event (too soon)')
        return
      }
      
      // Increase debounce to 5 seconds to handle system dialogs like screen share permission
      blurTimeout = setTimeout(() => {
        // Only track if window is still blurred after 5 seconds
        // This allows time for legitimate dialogs (screen share, camera permission, etc.)
        if (!document.hasFocus() && document.visibilityState === 'visible') {
          lastBlurTime = Date.now()
          trackViolation({
            type: 'window_lost_focus',
            severity: 'low', // Changed from medium to low
            details: 'Window lost focus for extended period'
          })
          console.log('⚠️ Window focus lost for more than 5 seconds')
        } else {
          console.log('✅ Focus loss was temporary (system dialog or quick switch)')
        }
        blurTimeout = null
      }, 5000) // Increased from 2 to 5 seconds
    }

    const focusHandler = () => {
      // Clear blur timeout when focus is regained
      if (blurTimeout) {
        clearTimeout(blurTimeout)
        blurTimeout = null
        console.log('✅ Focus regained, blur violation cancelled')
      }
    }

    document.addEventListener('visibilitychange', visibilityChangeHandler)
    window.addEventListener('blur', blurHandler)
    window.addEventListener('focus', focusHandler)
  }

  const initializeFullscreenMonitoring = () => {
    const enterFullscreen = () => {
      const elem = document.documentElement
      if (elem.requestFullscreen) {
        elem.requestFullscreen().catch(() => {})
      } else if (elem.webkitRequestFullscreen) {
        elem.webkitRequestFullscreen()
      } else if (elem.webkitEnterFullscreen) {
        elem.webkitEnterFullscreen()
      } else if (elem.msRequestFullscreen) {
        elem.msRequestFullscreen()
      }
    }

    fullscreenChangeHandler = () => {
      const isNowFullscreen = !!(
        document.fullscreenElement ||
        document.webkitFullscreenElement ||
        document.webkitCurrentFullScreenElement ||
        document.msFullscreenElement
      )

      isFullscreen.value = isNowFullscreen

      if (!isNowFullscreen && tabSwitchCount.value > 0) {
        trackViolation({
          type: 'fullscreen_exit',
          severity: 'critical',
          details: 'Exited fullscreen mode - attempting to cheat'
        })
        
        onViolation({
          type: 'fullscreen_exit',
          severity: 'critical',
          details: 'Exited fullscreen mode'
        })
        
        // Force back to fullscreen immediately
        setTimeout(enterFullscreen, 100)
      }
    }
    
    // Detect window minimize/resize
    window.addEventListener('resize', () => {
      if (document.hidden || window.outerWidth < window.screen.width - 100) {
        windowMinimized.value = true
        trackViolation({
          type: 'window_minimized',
          severity: 'critical',
          details: 'Window minimized or resized - potential cheating'
        })
        
        onViolation({
          type: 'window_minimized',
          severity: 'critical',
          details: 'Browser window minimized or resized'
        })
      } else {
        windowMinimized.value = false
      }
    })
    
    // Detect window blur (alt+tab, clicking outside)
    window.addEventListener('blur', () => {
      browserOutOfFocus.value = true
      trackViolation({
        type: 'window_lost_focus',
        severity: 'high',
        details: 'Switched to another window or application'
      })
      
      onViolation({
        type: 'window_lost_focus',
        severity: 'high',
        details: 'Lost browser focus - switched windows'
      })
    })
    
    window.addEventListener('focus', () => {
      browserOutOfFocus.value = false
    })

    document.addEventListener('fullscreenchange', fullscreenChangeHandler)
    document.addEventListener('webkitfullscreenchange', fullscreenChangeHandler)
    document.addEventListener('msfullscreenchange', fullscreenChangeHandler)

    // Force fullscreen immediately
    setTimeout(enterFullscreen, 1000)
    
    // Re-enforce fullscreen every 3 seconds if exited
    setInterval(() => {
      if (!isFullscreen.value) {
        enterFullscreen()
      }
    }, 3000)
  }

  const initializeKeyboardBlocking = () => {
    keyboardHandler = (e) => {
      const blocked = 
        e.key === 'F12' ||
        e.key === 'F11' ||
        e.key === 'PrintScreen' ||
        e.key === 'Meta' ||
        (e.ctrlKey && e.key === 'c') ||
        (e.ctrlKey && e.key === 'v') ||
        (e.ctrlKey && e.key === 'x') ||
        (e.ctrlKey && e.key === 'a') ||
        (e.ctrlKey && e.key === 'f') ||
        (e.ctrlKey && e.key === 'p') ||
        (e.ctrlKey && e.key === 's') ||
        (e.ctrlKey && e.key === 'u') ||
        (e.ctrlKey && e.shiftKey && e.key === 'I') ||
        (e.ctrlKey && e.shiftKey && e.key === 'J') ||
        (e.ctrlKey && e.shiftKey && e.key === 'C') ||
        e.metaKey

      if (blocked) {
        e.preventDefault()
        e.stopPropagation()
        
        onViolation({
          type: 'blocked_key',
          severity: 'medium',
          details: `Attempted blocked action`
        })
        
        return false
      }
    }

    contextMenuHandler = (e) => {
      e.preventDefault()
      onViolation({
        type: 'right_click',
        severity: 'low',
        details: 'Right-click attempted'
      })
    }

    document.addEventListener('keydown', keyboardHandler, true)
    document.addEventListener('contextmenu', contextMenuHandler)
  }

  const initializeMouseMonitoring = () => {
    let mouseLeftWindow = false
    let mouseLeaveTime = 0

    mouseLeaveHandler = () => {
      if (!mouseLeftWindow) {
        mouseLeftWindow = true
        mouseLeaveTime = Date.now()
        
        setTimeout(() => {
          if (mouseLeftWindow) {
            onViolation({
              type: 'mouse_left_window',
              severity: 'medium',
              details: 'Mouse left exam window'
            })
          }
        }, 2000)
      }
    }

    const mouseEnterHandler = () => {
      if (mouseLeftWindow) {
        const duration = Date.now() - mouseLeaveTime
        if (duration > 3000) {
          onViolation({
            type: 'mouse_away_extended',
            severity: 'high',
            details: `Mouse away for ${Math.round(duration / 1000)}s`
          })
        }
        mouseLeftWindow = false
      }
    }

    document.addEventListener('mouseleave', mouseLeaveHandler)
    document.addEventListener('mouseenter', mouseEnterHandler)
  }

  const initializeFaceDetection = async () => {
    try {
      console.log('🔍 Initializing MediaPipe face detection...')
      
      const vision = await FilesetResolver.forVisionTasks(
        'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm'
      )
      
      faceDetector.value = await FaceDetector.createFromOptions(vision, {
        baseOptions: {
          modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite',
          delegate: 'GPU'
        },
        runningMode: 'VIDEO',
        minDetectionConfidence: 0.5
      })

      modelStatus.value.mediapipe.loaded = true
      console.log('✅ MediaPipe face detector initialized')
      
      if (videoRef.value) {
        videoRef.value.addEventListener('loadeddata', () => {
          console.log('📹 Video ready, starting detection loop')
          setTimeout(() => startDetectionLoop(), 1000)
        })
      } else {
        setTimeout(() => startDetectionLoop(), 1000)
      }
    } catch (error) {
      console.error('❌ MediaPipe face detection initialization failed:', error)
      // Schedule retry
      setTimeout(() => retryModelInitialization('mediapipe', initializeFaceDetection), 3000)
    }
  }

  const initializeBlazeFaceModel = async () => {
    try {
      console.log('🔍 Initializing BlazeFace model...')
      await tf.ready()
      await tf.setBackend('webgl') // Force WebGL backend for better performance
      blazefaceModel.value = await blazeface.load()
      modelStatus.value.blazeface.loaded = true
      console.log('✅ BlazeFace model loaded')
    } catch (error) {
      console.error('❌ BlazeFace initialization failed:', error)
      modelStatus.value.blazeface.error = error.message
      
      // Try fallback to CPU backend
      try {
        console.log('⚠️ Retrying BlazeFace with CPU backend...')
        await tf.setBackend('cpu')
        blazefaceModel.value = await blazeface.load()
        modelStatus.value.blazeface.loaded = true
        console.log('✅ BlazeFace loaded (CPU fallback)')
      } catch (fallbackError) {
        console.error('❌ BlazeFace CPU fallback failed:', fallbackError)
        setTimeout(() => retryModelInitialization('blazeface', initializeBlazeFaceModel), 5000)
      }
    }
  }

  const initializeFaceLandmarksModel = async () => {
    try {
      console.log('🔍 Initializing Face Landmarks model for head pose & eye tracking...')
      await tf.ready()
      
      faceLandmarksModel.value = await faceLandmarksDetection.createDetector(
        faceLandmarksDetection.SupportedModels.MediaPipeFaceMesh,
        {
          runtime: 'tfjs',
          refineLandmarks: true,
          maxFaces: 2
        }
      )
      
      modelStatus.value.facelandmarks.loaded = true
      console.log('✅ Face Landmarks model loaded')
    } catch (error) {
      console.error('❌ Face Landmarks initialization failed:', error)
      modelStatus.value.facelandmarks.error = error.message
      
      // Try simplified version without refineLandmarks
      try {
        console.log('⚠️ Retrying Face Landmarks (simplified)...')
        faceLandmarksModel.value = await faceLandmarksDetection.createDetector(
          faceLandmarksDetection.SupportedModels.MediaPipeFaceMesh,
          {
            runtime: 'tfjs',
            refineLandmarks: false,
            maxFaces: 1
          }
        )
        modelStatus.value.facelandmarks.loaded = true
        console.log('✅ Face Landmarks loaded (simplified)')
      } catch (fallbackError) {
        console.error('❌ Face Landmarks simplified fallback failed:', fallbackError)
        setTimeout(() => retryModelInitialization('facelandmarks', initializeFaceLandmarksModel), 5000)
      }
    }
  }

  const initializeObjectDetection = async () => {
    try {
      console.log('🔍 Initializing COCO-SSD object detection...')
      await tf.ready()
      objectDetectionModel.value = await cocoSsd.load({
        base: 'lite_mobilenet_v2'
      })
      modelStatus.value.objectdetection.loaded = true
      console.log('✅ Object detection model loaded')
    } catch (error) {
      console.error('❌ Object detection initialization failed:', error)
      modelStatus.value.objectdetection.error = error.message
      
      // Try even lighter model
      try {
        console.log('⚠️ Retrying with mobilenet_v1...')
        objectDetectionModel.value = await cocoSsd.load({
          base: 'mobilenet_v1'
        })
        modelStatus.value.objectdetection.loaded = true
        console.log('✅ Object detection loaded (mobilenet_v1)')
      } catch (fallbackError) {
        console.error('❌ Object detection fallback failed:', fallbackError)
        // Continue without object detection - not critical
        console.log('ℹ️ Continuing without object detection')
      }
    }
  }

  const detectHeadPose = (landmarks) => {
    // Estimate head pose using key facial landmarks
    // Using nose tip, chin, left eye, right eye positions
    
    const noseTip = landmarks[4] // Nose tip landmark
    const chin = landmarks[152] // Chin landmark
    const leftEye = landmarks[33] // Left eye
    const rightEye = landmarks[263] // Right eye
    
    if (!noseTip || !chin || !leftEye || !rightEye) return null
    
    // Calculate relative positions
    const faceWidth = Math.abs(leftEye.x - rightEye.x)
    const faceHeight = Math.abs(noseTip.y - chin.y)
    
    // Estimate yaw (left-right rotation)
    const noseCenterX = (leftEye.x + rightEye.x) / 2
    const yaw = (noseTip.x - noseCenterX) / faceWidth
    
    // Estimate pitch (up-down rotation)
    const eyesY = (leftEye.y + rightEye.y) / 2
    const pitch = (noseTip.y - eyesY) / faceHeight
    
    // Estimate roll (tilt)
    const roll = Math.atan2(rightEye.y - leftEye.y, rightEye.x - leftEye.x)
    
    return { pitch, yaw, roll }
  }

  const detectEyeClosure = (landmarks) => {
    // Calculate Eye Aspect Ratio (EAR) for both eyes
    const calculateEAR = (eyeLandmarks) => {
      // Vertical distances
      const v1 = Math.hypot(
        eyeLandmarks[1].x - eyeLandmarks[5].x,
        eyeLandmarks[1].y - eyeLandmarks[5].y
      )
      const v2 = Math.hypot(
        eyeLandmarks[2].x - eyeLandmarks[4].x,
        eyeLandmarks[2].y - eyeLandmarks[4].y
      )
      
      // Horizontal distance
      const h = Math.hypot(
        eyeLandmarks[0].x - eyeLandmarks[3].x,
        eyeLandmarks[0].y - eyeLandmarks[3].y
      )
      
      return (v1 + v2) / (2.0 * h)
    }
    
    // Left eye landmarks (indices for MediaPipeFaceMesh)
    const leftEyeLandmarks = [
      landmarks[33], landmarks[160], landmarks[158],
      landmarks[133], landmarks[153], landmarks[144]
    ]
    
    // Right eye landmarks
    const rightEyeLandmarks = [
      landmarks[362], landmarks[385], landmarks[387],
      landmarks[263], landmarks[373], landmarks[380]
    ]
    
    if (leftEyeLandmarks.some(l => !l) || rightEyeLandmarks.some(l => !l)) {
      return false
    }
    
    const leftEAR = calculateEAR(leftEyeLandmarks)
    const rightEAR = calculateEAR(rightEyeLandmarks)
    const avgEAR = (leftEAR + rightEAR) / 2
    
    // EAR threshold (typically < 0.2 indicates closed eyes)
    return avgEAR < 0.2
  }

  const startDetectionLoop = () => {
    if (!videoRef.value || videoRef.value.readyState < 2) {
      console.warn('⚠️ Video not ready, retrying in 1 second...')
      setTimeout(() => startDetectionLoop(), 1000)
      return
    }

    console.log(`🎬 Starting comprehensive ML detection loop [Mode: ${detectionMode.value.toUpperCase()}]`)
    
    detectionInterval.value = setInterval(async () => {
      if (!videoRef.value) return
      
      if (videoRef.value.readyState < 2 || videoRef.value.paused) return

      try {
        let faceDetected = false
        
        // 1. MediaPipe Face Detection (face count) - Primary
        if (faceDetector.value && modelStatus.mediapipe.loaded) {
          const now = performance.now()
          const detections = faceDetector.value.detectForVideo(
            videoRef.value,
            now
          )

          const faceCount = detections.detections.length
          
          if (faceCount === 0) {
            consecutiveNoFace.value++
            if (consecutiveNoFace.value >= 2) {
              onViolation({
                type: 'no_face_detected',
                severity: 'high',
                details: 'No face visible in camera'
              })
            }
          } else if (faceCount > 1) {
            consecutiveNoFace.value = 0
            onViolation({
              type: 'multiple_faces',
              severity: 'critical',
              details: `${faceCount} faces detected`
            })
            faceDetected = true
          } else {
            consecutiveNoFace.value = 0
            faceDetected = true
          }
        }

        // 2. BlazeFace for additional face validation - Fallback if MediaPipe failed
        if (blazefaceModel.value && modelStatus.blazeface.loaded) {
          const predictions = await blazefaceModel.value.estimateFaces(videoRef.value, false)
          
          if (predictions.length > 0) {
            const face = predictions[0]
            faceDetected = true
            
            // Update face detection status for UI
            faceDetectionStatus.value.faceDetected = true
            faceDetectionStatus.value.faceBoundingBox = {
              x: face.topLeft[0],
              y: face.topLeft[1],
              width: face.bottomRight[0] - face.topLeft[0],
              height: face.bottomRight[1] - face.topLeft[1]
            }
            
            // Track face position for movement detection
            if (lastFacePosition.value) {
              const displacement = Math.hypot(
                face.topLeft[0] - lastFacePosition.value.topLeft[0],
                face.topLeft[1] - lastFacePosition.value.topLeft[1]
              )
              
              if (displacement > 100) {
                onViolation({
                  type: 'excessive_movement',
                  severity: 'medium',
                  details: 'Significant face movement detected'
                })
              }
            }
            
            lastFacePosition.value = face
          } else {
            faceDetectionStatus.value.faceDetected = false
            faceDetectionStatus.value.faceBoundingBox = null
          }
        }

        // 3. Face Landmarks for head pose and eye tracking
        if (faceLandmarksModel.value && modelStatus.facelandmarks.loaded) {
          const faces = await faceLandmarksModel.value.estimateFaces(videoRef.value)
          
          if (faces.length > 0) {
            const face = faces[0]
            const keypoints = face.keypoints
            faceDetected = true
            
            // Head pose estimation with stricter thresholds
            const headPose = detectHeadPose(keypoints)
            if (headPose) {
              // More aggressive threshold: 20% instead of 30%
              const lookingAwayThreshold = 0.20
              
              if (Math.abs(headPose.yaw) > lookingAwayThreshold || 
                  Math.abs(headPose.pitch) > lookingAwayThreshold) {
                consecutiveLookingAway.value++
                faceDetectionStatus.value.lookingAtScreen = false
                
                // Detect after 2 consecutive frames instead of 3
                if (consecutiveLookingAway.value >= 2) {
                  trackViolation({
                    type: 'looking_away',
                    severity: 'high',
                    details: `Head turned away (yaw: ${(headPose.yaw * 100).toFixed(0)}%, pitch: ${(headPose.pitch * 100).toFixed(0)}%)`
                  })
                  consecutiveLookingAway.value = 0
                }
              } else {
                consecutiveLookingAway.value = 0
                faceDetectionStatus.value.lookingAtScreen = true
              }
              
              lastHeadPose.value = headPose
            }
            
            // Eye closure detection with stricter threshold  
            const eyesClosed = detectEyeClosure(keypoints)
            faceDetectionStatus.value.eyesOpen = !eyesClosed
            
            if (eyesClosed) {
              eyeClosedCount.value++
              
              // Detect after 3 frames instead of 5
              if (eyeClosedCount.value >= 3) {
                trackViolation({
                  type: 'eyes_closed',
                  severity: 'medium',
                  details: 'Eyes closed for extended period'
                })
                eyeClosedCount.value = 0
              }
            } else {
              eyeClosedCount.value = 0
            }
          }
        }

        // 4. Object Detection for suspicious items - CRITICAL
        if (objectDetectionModel.value && modelStatus.objectdetection.loaded) {
          const predictions = await objectDetectionModel.value.detect(videoRef.value)
          
          const suspiciousClasses = ['cell phone', 'book', 'laptop', 'tablet', 'tv', 'monitor', 'keyboard', 'mouse']
          const detectedSuspicious = predictions.filter(p => 
            suspiciousClasses.some(cls => p.class.toLowerCase().includes(cls))
          )
          
          if (detectedSuspicious.length > 0) {
            const objects = detectedSuspicious.map(p => p.class).join(', ')
            
            // Check if this is a new detection (not already reported)
            const newDetection = !suspiciousObjects.value.some(
              obj => detectedSuspicious.some(d => d.class === obj.class)
            )
            
            if (newDetection) {
              trackViolation({
                type: 'suspicious_object',
                severity: 'critical',
                details: `Detected: ${objects} - IMMEDIATE REVIEW REQUIRED`
              })
              
              suspiciousObjects.value = detectedSuspicious
            }
          } else {
            suspiciousObjects.value = []
          }
        }

        // 5. Fallback Detection - Use when ALL ML models fail
        if (detectionMode.value === 'manual' && !faceDetected) {
          const hasFace = fallbackFaceDetection()
          
          if (!hasFace) {
            consecutiveNoFace.value++
            if (consecutiveNoFace.value >= 2) {
              onViolation({
                type: 'no_face_detected',
                severity: 'high',
                details: 'No face visible (fallback detection)'
              })
            }
          } else {
            consecutiveNoFace.value = 0
          }
          
          console.log('⚠️ Using fallback detection - ML models unavailable')
        }

      } catch (error) {
        console.error('⚠️ Detection error:', error)
        
        // On repeated errors, use fallback detection
        if (detectionMode.value !== 'manual') {
          console.log('🔄 Switching to fallback detection due to errors')
          try {
            const hasFace = fallbackFaceDetection()
            if (!hasFace) {
              consecutiveNoFace.value++
              if (consecutiveNoFace.value >= 2) {
                onViolation({
                  type: 'no_face_detected',
                  severity: 'high',
                  details: 'No face visible (error fallback)'
                })
              }
            } else {
              consecutiveNoFace.value = 0
            }
          } catch (fallbackError) {
            console.error('❌ Fallback detection also failed:', fallbackError)
          }
        }
      }
    }, 3000) // Check every 3 seconds
  }

  const captureFrame = () => {
    if (!videoRef.value) return null

    const canvas = document.createElement('canvas')
    canvas.width = videoRef.value.videoWidth
    canvas.height = videoRef.value.videoHeight
    const ctx = canvas.getContext('2d')
    ctx.drawImage(videoRef.value, 0, 0)
    
    return canvas.toDataURL('image/jpeg', 0.7)
  }

  const cleanup = () => {
    if (detectionInterval.value) {
      clearInterval(detectionInterval.value)
    }
    if (stream.value) {
      stream.value.getTracks().forEach(track => track.stop())
    }
    if (audioContext.value) {
      audioContext.value.close()
    }
    if (faceDetector.value) {
      faceDetector.value.close()
    }

    // Dispose TensorFlow models
    if (blazefaceModel.value) {
      blazefaceModel.value = null
    }
    if (faceLandmarksModel.value) {
      faceLandmarksModel.value.dispose()
      faceLandmarksModel.value = null
    }
    if (objectDetectionModel.value) {
      objectDetectionModel.value.dispose()
      objectDetectionModel.value = null
    }

    // Dispose TensorFlow tensors
    tf.disposeVariables()

    // Clear blur timeout if exists
    if (blurTimeout) {
      clearTimeout(blurTimeout)
      blurTimeout = null
    }

    if (visibilityChangeHandler) {
      document.removeEventListener('visibilitychange', visibilityChangeHandler)
    }
    if (blurHandler) {
      window.removeEventListener('blur', blurHandler)
      window.removeEventListener('focus', blurHandler) // Also remove focus handler
    }
    if (fullscreenChangeHandler) {
      document.removeEventListener('fullscreenchange', fullscreenChangeHandler)
      document.removeEventListener('webkitfullscreenchange', fullscreenChangeHandler)
      document.removeEventListener('msfullscreenchange', fullscreenChangeHandler)
    }
    if (keyboardHandler) {
      document.removeEventListener('keydown', keyboardHandler, true)
    }
    if (contextMenuHandler) {
      document.removeEventListener('contextmenu', contextMenuHandler)
    }
    if (mouseLeaveHandler) {
      document.removeEventListener('mouseleave', mouseLeaveHandler)
    }

    if (document.fullscreenElement) {
      document.exitFullscreen().catch(() => {})
    }
  }

  return {
    videoRef,
    audioLevel,
    isMobile,
    detectionMode,
    modelStatus,
    faceDetectionStatus,
    initializeCamera,
    captureFrame,
    cleanup
  }
}
