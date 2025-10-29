<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
    <!-- Header -->
    <header class="bg-white shadow-md sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-8 py-4 flex justify-between items-center">
        <router-link to="/" class="text-2xl font-bold text-indigo-600">
          🎓 CauchyMentor
        </router-link>
        <div class="flex items-center gap-4">
          <router-link 
            to="/teacher/dashboard" 
            class="text-gray-600 hover:text-indigo-600 font-medium"
          >
            Dashboard
          </router-link>
          <span class="text-gray-700">{{ authStore.user?.full_name }}</span>
          <button 
            @click="logout" 
            class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
          >
            Logout
          </button>
        </div>
      </div>
    </header>

    <div class="max-w-4xl mx-auto px-6 py-12">
      <!-- Success Message -->
      <div v-if="testCreated" class="bg-green-50 border-2 border-green-500 rounded-xl p-8 mb-8 text-center">
        <div class="text-6xl mb-4">✅</div>
        <h2 class="text-3xl font-bold text-green-800 mb-4">Test Created Successfully!</h2>
        <div class="bg-white rounded-lg p-6 mb-6 border-2 border-green-300">
          <p class="text-gray-600 mb-2">Share this code with students:</p>
          <div class="text-5xl font-bold text-indigo-600 tracking-wider font-mono">
            {{ createdTestCode }}
          </div>
        </div>
        <div class="flex gap-4 justify-center">
          <button 
            @click="copyTestCode" 
            class="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-semibold"
          >
            📋 Copy Code
          </button>
          <button 
            @click="viewMonitoring" 
            class="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-semibold"
          >
            📺 Monitor Test
          </button>
          <button 
            @click="createAnother" 
            class="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 font-semibold"
          >
            ➕ Create Another
          </button>
        </div>
      </div>

      <!-- Test Creation Form -->
      <div v-else class="bg-white rounded-2xl shadow-xl p-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">📝 Create Proctored Test</h1>
        <p class="text-gray-600 mb-8">Students will join using a 4-digit code with camera and screen monitoring</p>

        <form @submit.prevent="createTest" class="space-y-6">
          <!-- Basic Info -->
          <div class="border-b pb-6">
            <h3 class="text-xl font-semibold text-gray-900 mb-4">Basic Information</h3>
            
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Test Title *
                </label>
                <input
                  v-model="testForm.title"
                  type="text"
                  placeholder="e.g., Midterm Exam - Calculus"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  v-model="testForm.description"
                  rows="3"
                  placeholder="Describe what this test covers..."
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                ></textarea>
              </div>

              <div class="grid md:grid-cols-3 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Duration (minutes) *
                  </label>
                  <input
                    v-model.number="testForm.duration_minutes"
                    type="number"
                    min="5"
                    max="300"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    required
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Total Marks *
                  </label>
                  <input
                    v-model.number="testForm.total_marks"
                    type="number"
                    min="1"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    required
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Passing Marks *
                  </label>
                  <input
                    v-model.number="testForm.passing_marks"
                    type="number"
                    min="1"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    required
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Proctoring Settings -->
          <div class="border-b pb-6">
            <h3 class="text-xl font-semibold text-gray-900 mb-4">🎥 Proctoring Settings</h3>
            
            <div class="space-y-4">
              <label class="flex items-start gap-3 p-4 border-2 border-indigo-200 rounded-lg bg-indigo-50 cursor-pointer">
                <input
                  v-model="testForm.proctoring_enabled"
                  type="checkbox"
                  class="mt-1 w-5 h-5 text-indigo-600"
                  checked
                  disabled
                />
                <div>
                  <div class="font-semibold text-gray-900">Enable Proctoring (Required)</div>
                  <div class="text-sm text-gray-600">Students must share camera and screen</div>
                </div>
              </label>

              <label class="flex items-start gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-indigo-300 cursor-pointer">
                <input
                  v-model="testForm.require_webcam"
                  type="checkbox"
                  class="mt-1 w-5 h-5 text-indigo-600"
                />
                <div>
                  <div class="font-semibold text-gray-900">Require Webcam</div>
                  <div class="text-sm text-gray-600">Student must enable webcam to start test</div>
                </div>
              </label>

              <label class="flex items-start gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-indigo-300 cursor-pointer">
                <input
                  v-model="testForm.detect_multiple_faces"
                  type="checkbox"
                  class="mt-1 w-5 h-5 text-indigo-600"
                />
                <div>
                  <div class="font-semibold text-gray-900">Detect Multiple Faces</div>
                  <div class="text-sm text-gray-600">Alert if more than one person detected</div>
                </div>
              </label>

              <label class="flex items-start gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-indigo-300 cursor-pointer">
                <input
                  v-model="testForm.allow_tab_switch"
                  type="checkbox"
                  class="mt-1 w-5 h-5 text-indigo-600"
                />
                <div>
                  <div class="font-semibold text-gray-900">Allow Tab Switching</div>
                  <div class="text-sm text-gray-600">Students can switch tabs without violations</div>
                </div>
              </label>
            </div>
          </div>

          <!-- Questions -->
          <div>
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-xl font-semibold text-gray-900">Questions</h3>
              <div class="flex gap-2">
                <button 
                  type="button"
                  @click="showAIModal = true"
                  class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-semibold"
                >
                  ✨ Generate with AI
                </button>
                <button 
                  type="button"
                  @click="addQuestion"
                  class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-semibold"
                >
                  + Add Question
                </button>
              </div>
            </div>

            <div v-if="testForm.questions.length === 0" class="text-center py-8 text-gray-500">
              No questions added yet. Click "+ Add Question" or "Generate with AI" to start.
            </div>

            <div v-else class="space-y-4">
              <div 
                v-for="(question, index) in testForm.questions" 
                :key="index"
                class="border-2 border-gray-200 rounded-lg p-6 bg-gray-50"
              >
                <div class="flex items-start justify-between mb-4">
                  <h4 class="font-semibold text-gray-900">Question {{ index + 1 }}</h4>
                  <button 
                    type="button"
                    @click="removeQuestion(index)"
                    class="text-red-600 hover:text-red-700"
                  >
                    🗑️ Remove
                  </button>
                </div>

                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                      Question Type
                    </label>
                    <select
                      v-model="question.question_type"
                      class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    >
                      <option value="multiple_choice">Multiple Choice</option>
                      <option value="true_false">True/False</option>
                      <option value="short_answer">Short Answer</option>
                    </select>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                      Question Text *
                    </label>
                    <textarea
                      v-model="question.question_text"
                      rows="3"
                      placeholder="Enter your question..."
                      class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      required
                    ></textarea>
                  </div>

                  <!-- Multiple Choice Options -->
                  <div v-if="question.question_type === 'multiple_choice'" class="space-y-2">
                    <label class="block text-sm font-medium text-gray-700">Options *</label>
                    <div v-for="(option, optIndex) in question.options" :key="optIndex" class="flex gap-2">
                      <input
                        v-model="question.options[optIndex]"
                        type="text"
                        placeholder="Option text"
                        class="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
                        required
                      />
                      <button 
                        v-if="question.options.length > 2"
                        type="button"
                        @click="question.options.splice(optIndex, 1)"
                        class="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg"
                      >
                        ✕
                      </button>
                    </div>
                    <button 
                      type="button"
                      @click="question.options.push('')"
                      class="text-sm text-indigo-600 hover:text-indigo-700"
                    >
                      + Add Option
                    </button>
                  </div>

                  <!-- Correct Answer -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                      Correct Answer *
                    </label>
                    <input
                      v-if="question.question_type !== 'multiple_choice'"
                      v-model="question.correct_answer"
                      type="text"
                      placeholder="Enter correct answer"
                      class="w-full px-4 py-3 border border-gray-300 rounded-lg"
                      required
                    />
                    <select
                      v-else
                      v-model="question.correct_answer"
                      class="w-full px-4 py-3 border border-gray-300 rounded-lg"
                      required
                    >
                      <option value="">Select correct option</option>
                      <option v-for="(opt, i) in question.options" :key="i" :value="opt">
                        {{ opt || `Option ${i + 1}` }}
                      </option>
                    </select>
                  </div>

                  <div class="grid md:grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">
                        Marks
                      </label>
                      <input
                        v-model.number="question.marks"
                        type="number"
                        min="1"
                        class="w-full px-4 py-3 border border-gray-300 rounded-lg"
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">
                        Difficulty
                      </label>
                      <select
                        v-model="question.difficulty"
                        class="w-full px-4 py-3 border border-gray-300 rounded-lg"
                      >
                        <option value="easy">Easy</option>
                        <option value="medium">Medium</option>
                        <option value="hard">Hard</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Submit Button -->
          <div class="flex gap-4 pt-6">
            <button 
              type="submit"
              :disabled="creating || testForm.questions.length === 0"
              class="flex-1 px-6 py-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-semibold text-lg"
            >
              <span v-if="creating">Creating Test...</span>
              <span v-else>🚀 Create Test & Generate Code</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- AI Generation Modal -->
    <div v-if="showAIModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-2xl p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h3 class="text-2xl font-bold mb-4">✨ Generate Questions with AI</h3>
        
        <!-- AI Mode Tabs -->
        <div class="flex border-b mb-6">
          <button 
            @click="aiGenerationMode = 'topic'" 
            type="button"
            :class="['px-4 py-2 font-semibold', aiGenerationMode === 'topic' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-gray-500']">
            From Topic
          </button>
          <button 
            @click="aiGenerationMode = 'pdf'" 
            type="button"
            :class="['px-4 py-2 font-semibold', aiGenerationMode === 'pdf' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-gray-500']">
            From PDF/Material
          </button>
        </div>

        <!-- Topic Mode -->
        <div v-if="aiGenerationMode === 'topic'" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Topic</label>
            <input v-model="aiForm.topic" type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg"
              placeholder="e.g., Calculus Derivatives" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Number of Questions</label>
            <input v-model.number="aiForm.num_questions" type="number" min="1" max="20"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
            <select v-model="aiForm.difficulty"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg">
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
        </div>

        <!-- PDF Mode -->
        <div v-else class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Upload PDF</label>
            <div @click="$refs.pdfInput.click()" @dragover.prevent="pdfDragOver = true" @dragleave.prevent="pdfDragOver = false" @drop.prevent="handlePdfDrop"
              :class="['border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors', pdfDragOver ? 'border-purple-500 bg-purple-50' : 'border-gray-300 hover:border-gray-400']">
              <input ref="pdfInput" type="file" accept=".pdf" @change="handlePdfSelect" class="hidden" />
              <div v-if="!uploadedPdf">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <div class="mt-2 text-sm text-gray-600">
                  <span class="font-semibold text-purple-600">Click to upload</span> or drag and drop
                </div>
                <div class="text-xs text-gray-500 mt-1">PDF only (max 10MB)</div>
              </div>
              <div v-else class="flex items-center justify-center gap-3">
                <svg class="h-8 w-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ uploadedPdf.name }}</p>
                  <p class="text-xs text-gray-500">{{ formatFileSize(uploadedPdf.size) }}</p>
                </div>
                <button @click.stop="uploadedPdf = null" class="text-red-600 hover:text-red-700">
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <div v-if="uploadedPdf">
            <label class="block text-sm font-medium text-gray-700 mb-2">Number of Questions</label>
            <input v-model.number="aiForm.num_questions" type="number" min="1" max="20"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg" />
          </div>

          <div v-if="uploadedPdf">
            <label class="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
            <select v-model="aiForm.difficulty"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg">
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
        </div>

        <!-- Progress Bar -->
        <div v-if="aiLoading && aiGenerationMode === 'pdf'" class="mt-6">
          <div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div class="bg-purple-600 h-2 transition-all duration-300" :style="{ width: uploadProgress + '%' }"></div>
          </div>
          <p class="text-sm text-gray-600 mt-2 text-center">
            {{ uploadProgress < 50 ? 'Uploading and extracting text...' : uploadProgress < 90 ? 'Generating questions...' : 'Almost done!' }}
          </p>
        </div>

        <!-- Buttons -->
        <div class="flex gap-3 mt-6">
          <button type="button" @click="closeAIModal"
            class="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">
            Cancel
          </button>
          <button type="button" @click="generateWithAI" :disabled="aiLoading || (aiGenerationMode === 'pdf' && !uploadedPdf)"
            class="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed">
            {{ aiLoading ? 'Generating...' : 'Generate Questions' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'
import { useToast } from 'vue-toastification'
import { backupAiService } from '../services/backupAiService'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const testForm = ref({
  title: '',
  description: '',
  duration_minutes: 60,
  total_marks: 100,
  passing_marks: 40,
  proctoring_enabled: true,
  require_webcam: true,
  detect_multiple_faces: true,
  allow_tab_switch: false,
  questions: []
})

const creating = ref(false)
const testCreated = ref(false)
const createdTestCode = ref('')
const createdTestId = ref(null)

// AI Generation
const showAIModal = ref(false)
const aiGenerationMode = ref('topic')
const aiLoading = ref(false)
const uploadProgress = ref(0)
const uploadedPdf = ref(null)
const pdfDragOver = ref(false)
const aiForm = ref({
  topic: '',
  num_questions: 10,
  difficulty: 'medium'
})

const addQuestion = () => {
  testForm.value.questions.push({
    question_type: 'multiple_choice',
    question_text: '',
    options: ['', '', '', ''],
    correct_answer: '',
    marks: 1,
    difficulty: 'medium'
  })
}

const removeQuestion = (index) => {
  testForm.value.questions.splice(index, 1)
}

const createTest = async () => {
  if (testForm.value.questions.length === 0) {
    toast.error('Add at least one question')
    return
  }

  creating.value = true
  try {
    const response = await api.post('/tests/create', testForm.value)
    createdTestCode.value = response.data.test_code
    createdTestId.value = response.data.test_id
    testCreated.value = true
    toast.success('Test created successfully!')
  } catch (error) {
    console.error('Failed to create test:', error)
    toast.error(error.response?.data?.detail || 'Failed to create test')
  } finally {
    creating.value = false
  }
}

const copyTestCode = () => {
  navigator.clipboard.writeText(createdTestCode.value)
  toast.success('Test code copied to clipboard!')
}

const viewMonitoring = () => {
  router.push(`/test-monitor/${createdTestId.value}`)
}

const createAnother = () => {
  testCreated.value = false
  testForm.value = {
    title: '',
    description: '',
    duration_minutes: 60,
    total_marks: 100,
    passing_marks: 40,
    proctoring_enabled: true,
    require_webcam: true,
    detect_multiple_faces: true,
    allow_tab_switch: false,
    questions: []
  }
  createdTestCode.value = ''
  createdTestId.value = null
}

// AI Functions
const handlePdfSelect = (event) => {
  const file = event.target.files[0]
  if (file && file.type === 'application/pdf') {
    if (file.size > 10 * 1024 * 1024) {
      toast.error('File size must be less than 10MB')
      return
    }
    uploadedPdf.value = file
  } else {
    toast.error('Please select a PDF file')
  }
}

const handlePdfDrop = (event) => {
  pdfDragOver.value = false
  const file = event.dataTransfer.files[0]
  if (file && file.type === 'application/pdf') {
    if (file.size > 10 * 1024 * 1024) {
      toast.error('File size must be less than 10MB')
      return
    }
    uploadedPdf.value = file
  } else {
    toast.error('Please drop a PDF file')
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const closeAIModal = () => {
  showAIModal.value = false
  uploadedPdf.value = null
  uploadProgress.value = 0
  aiGenerationMode.value = 'topic'
}

const generateWithAI = async () => {
  aiLoading.value = true
  try {
    if (aiGenerationMode.value === 'pdf') {
      // PDF mode
      if (!uploadedPdf.value) {
        toast.error('Please upload a PDF file')
        aiLoading.value = false
        return
      }

      try {
        // Try backend first
        uploadProgress.value = 10
        const formData = new FormData()
        formData.append('file', uploadedPdf.value)
        formData.append('material_name', uploadedPdf.value.name)
        formData.append('material_type', 'notes')

        uploadProgress.value = 30
        const uploadResponse = await api.post('/ai-materials/upload-material', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })

        uploadProgress.value = 50
        const materialId = uploadResponse.data.id

        // Generate questions from PDF
        uploadProgress.value = 60
        const questionsResponse = await api.post('/ai-materials/generate-questions', {
          material_id: materialId,
          num_questions: aiForm.value.num_questions,
          difficulty: aiForm.value.difficulty,
          question_types: ['mcq', 'true_false']
        })

        uploadProgress.value = 90

        // Add questions to form
        questionsResponse.data.questions.forEach(q => {
          // Normalize question type
          const qType = q.type?.toLowerCase() || 'mcq'
          const isTrueFalse = qType.includes('true') || qType.includes('false') || qType === 'true_false'
          
          testForm.value.questions.push({
            question_type: isTrueFalse ? 'true_false' : 'multiple_choice',
            question_text: q.question,
            options: q.options || (isTrueFalse ? ['True', 'False'] : ['', '', '', '']),
            correct_answer: q.correct_answer,
            marks: q.points || 2,
            difficulty: aiForm.value.difficulty
          })
        })

        uploadProgress.value = 100
        toast.success(`Generated ${questionsResponse.data.questions.length} questions!`)
      } catch (backendError) {
        console.error('Backend failed, trying fallback AI:', backendError)
        
        // Fallback: Use browser-based AI
        if (!backupAiService.isAvailable()) {
          throw new Error('Backend unavailable and no fallback AI configured. Please add VITE_GROQ_API_KEY to .env')
        }

        // Note: PDF text extraction in browser is limited
        // For production, use backend OCR service
        throw new Error('PDF processing requires backend server. Please ensure backend is running on port 8000. Error: ' + (backendError.response?.data?.detail || backendError.message))
      }
    } else {
      // Topic mode
      if (!aiForm.value.topic) {
        toast.error('Please enter a topic')
        aiLoading.value = false
        return
      }

      try {
        // Try backend first
        const response = await api.post('/ai/generate-quiz', {
          topic: aiForm.value.topic,
          num_questions: aiForm.value.num_questions,
          difficulty: aiForm.value.difficulty
        })

        response.data.questions.forEach(q => {
          testForm.value.questions.push({
            question_type: 'multiple_choice',
            question_text: q.question_text || q.question,
            options: Object.values(q.options || {}),
            correct_answer: q.correct_answer,
            marks: q.marks || 1,
            difficulty: q.difficulty || aiForm.value.difficulty
          })
        })

        toast.success(`Generated ${response.data.questions.length} questions!`)
      } catch (backendError) {
        console.error('Backend failed, trying fallback AI:', backendError)
        
        // Fallback: Use browser-based AI
        if (!backupAiService.isAvailable()) {
          throw new Error('Backend unavailable and no fallback AI configured. Please add VITE_GROQ_API_KEY to .env')
        }

        toast.warning('Using fallback AI (backend unavailable)...')
        
        const questions = await backupAiService.generateQuestions(
          aiForm.value.topic,
          aiForm.value.num_questions,
          aiForm.value.difficulty
        )

        questions.forEach(q => {
          // Normalize question type
          const qType = q.type?.toLowerCase() || 'mcq'
          const isTrueFalse = qType.includes('true') || qType.includes('false') || qType === 'true_false'
          
          testForm.value.questions.push({
            question_type: isTrueFalse ? 'true_false' : 'multiple_choice',
            question_text: q.question,
            options: q.options || (isTrueFalse ? ['True', 'False'] : ['', '', '', '']),
            correct_answer: q.correct_answer,
            marks: q.points || 1,
            difficulty: aiForm.value.difficulty
          })
        })

        toast.success(`Generated ${questions.length} questions!`)
      }
    }

    closeAIModal()
  } catch (error) {
    console.error('Failed to generate questions:', error)
    toast.error(error.response?.data?.detail || error.message || 'Failed to generate questions')
    uploadProgress.value = 0
  } finally {
    aiLoading.value = false
  }
}

const logout = () => {
  authStore.logout()
  router.push('/')
}
</script>
