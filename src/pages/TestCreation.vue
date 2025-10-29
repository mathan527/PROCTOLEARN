<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100">
    <div class="max-w-5xl mx-auto px-6 py-8">
      <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900">Create New Test</h1>
        <p class="text-gray-600 mt-2">Set up a test with manual or AI-generated questions</p>
      </div>

      <div class="bg-white rounded-xl shadow-lg p-8">
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Test Title</label>
              <input v-model="form.title" type="text" required
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Calculus Midterm" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Duration (minutes)</label>
              <input v-model.number="form.duration" type="number" required min="1"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="60" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Total Marks</label>
              <input v-model.number="form.total_marks" type="number" required min="1"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="100" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Passing Marks</label>
              <input v-model.number="form.passing_marks" type="number" required min="1"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="40" />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
            <textarea v-model="form.description" rows="3"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              placeholder="Test instructions and details..."></textarea>
          </div>

          <div class="border-t pt-6">
            <h3 class="text-lg font-bold text-gray-900 mb-4">Proctoring Settings</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <label class="flex items-center gap-3 p-4 border-2 rounded-lg cursor-pointer"
                :class="form.enable_proctoring ? 'border-blue-500 bg-blue-50' : 'border-gray-200'">
                <input type="checkbox" v-model="form.enable_proctoring" class="w-5 h-5" />
                <div>
                  <p class="font-semibold text-gray-900">Enable Proctoring</p>
                  <p class="text-sm text-gray-600">Monitor students via camera</p>
                </div>
              </label>

              <label class="flex items-center gap-3 p-4 border-2 rounded-lg cursor-pointer"
                :class="form.enable_face_detection ? 'border-blue-500 bg-blue-50' : 'border-gray-200'">
                <input type="checkbox" v-model="form.enable_face_detection" class="w-5 h-5"
                  :disabled="!form.enable_proctoring" />
                <div>
                  <p class="font-semibold text-gray-900">Face Detection</p>
                  <p class="text-sm text-gray-600">Detect face presence</p>
                </div>
              </label>

              <label class="flex items-center gap-3 p-4 border-2 rounded-lg cursor-pointer"
                :class="form.enable_tab_switch_detection ? 'border-blue-500 bg-blue-50' : 'border-gray-200'">
                <input type="checkbox" v-model="form.enable_tab_switch_detection" class="w-5 h-5"
                  :disabled="!form.enable_proctoring" />
                <div>
                  <p class="font-semibold text-gray-900">Tab Switch Detection</p>
                  <p class="text-sm text-gray-600">Track window changes</p>
                </div>
              </label>

              <label class="flex items-center gap-3 p-4 border-2 rounded-lg cursor-pointer"
                :class="form.enable_audio_monitoring ? 'border-blue-500 bg-blue-50' : 'border-gray-200'">
                <input type="checkbox" v-model="form.enable_audio_monitoring" class="w-5 h-5"
                  :disabled="!form.enable_proctoring" />
                <div>
                  <p class="font-semibold text-gray-900">Audio Monitoring</p>
                  <p class="text-sm text-gray-600">Monitor audio levels</p>
                </div>
              </label>
            </div>

            <!-- Admission Mode Selection -->
            <div class="mt-6">
              <label class="block text-sm font-medium text-gray-700 mb-3">Student Admission Mode</label>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <label class="flex items-start gap-3 p-4 border-2 rounded-lg cursor-pointer transition-all"
                  :class="form.admission_mode === 'auto_admit' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-300'">
                  <input type="radio" v-model="form.admission_mode" value="auto_admit" class="mt-1 w-5 h-5" />
                  <div>
                    <p class="font-semibold text-gray-900">🚀 Auto Admit</p>
                    <p class="text-sm text-gray-600">Students can start test immediately after joining</p>
                  </div>
                </label>

                <label class="flex items-start gap-3 p-4 border-2 rounded-lg cursor-pointer transition-all"
                  :class="form.admission_mode === 'manual_approval' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-300'">
                  <input type="radio" v-model="form.admission_mode" value="manual_approval" class="mt-1 w-5 h-5" />
                  <div>
                    <p class="font-semibold text-gray-900">✋ Manual Approval</p>
                    <p class="text-sm text-gray-600">Students wait in waiting room until teacher approves them</p>
                  </div>
                </label>
              </div>
            </div>
          </div>

          <div class="border-t pt-6">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-bold text-gray-900">Questions</h3>
              <div class="flex gap-2">
                <button type="button" @click="showAIModal = true"
                  class="px-4 py-2 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700">
                  ✨ Generate with AI
                </button>
                <button type="button" @click="addQuestion"
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700">
                  + Add Question
                </button>
              </div>
            </div>

            <div v-if="form.questions.length === 0" class="text-center py-8 text-gray-500">
              No questions added yet. Click "Add Question" or "Generate with AI"
            </div>

            <div v-else class="space-y-4">
              <div v-for="(question, idx) in form.questions" :key="idx"
                class="border-2 border-gray-200 rounded-lg p-4">
                <div class="flex justify-between items-start mb-4">
                  <span class="font-bold text-gray-900">Question {{ idx + 1 }}</span>
                  <button type="button" @click="removeQuestion(idx)"
                    class="text-red-600 hover:text-red-700 font-semibold">
                    Remove
                  </button>
                </div>

                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Question Type</label>
                    <select v-model="question.question_type"
                      class="w-full px-4 py-2 border border-gray-300 rounded-lg">
                      <option value="multiple_choice">Multiple Choice</option>
                      <option value="true_false">True/False</option>
                      <option value="short_answer">Short Answer</option>
                      <option value="essay">Essay</option>
                    </select>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Question Text</label>
                    <textarea v-model="question.text" required rows="2"
                      class="w-full px-4 py-2 border border-gray-300 rounded-lg resize-none"
                      placeholder="Enter question text..."></textarea>
                  </div>

                  <div v-if="question.question_type === 'multiple_choice' || question.question_type === 'true_false'">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Options (comma-separated)</label>
                    <input v-model="question.optionsText" type="text"
                      class="w-full px-4 py-2 border border-gray-300 rounded-lg"
                      :placeholder="question.question_type === 'true_false' ? 'True, False' : 'Option A, Option B, Option C, Option D'" />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Correct Answer</label>
                    <input v-model="question.correct_answer" type="text"
                      class="w-full px-4 py-2 border border-gray-300 rounded-lg"
                      placeholder="Enter correct answer..." />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Marks</label>
                    <input v-model.number="question.marks" type="number" required min="1"
                      class="w-full px-4 py-2 border border-gray-300 rounded-lg" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="flex justify-end gap-4 pt-6 border-t">
            <button type="button" @click="$router.back()"
              class="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300">
              Cancel
            </button>
            <button type="submit" :disabled="loading || form.questions.length === 0"
              class="px-8 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed">
              {{ loading ? 'Creating...' : 'Create Test' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showAIModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-2xl p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h3 class="text-2xl font-bold mb-4">Generate Questions with AI</h3>
        
        <!-- Option Tabs -->
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
              <div v-else class="flex items-center justify-center space-x-3">
                <svg class="h-8 w-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <div class="text-left">
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

          <!-- Auto-create option for PDF mode -->
          <div v-if="uploadedPdf" class="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="autoCreateTest" class="w-4 h-4 text-purple-600 rounded" />
              <span class="text-sm font-medium text-gray-700">
                Auto-create and save test immediately (skip review)
              </span>
            </label>
            <p class="text-xs text-gray-500 mt-1 ml-6">
              Questions will be generated and test will be created automatically
            </p>
          </div>

          <div v-if="uploadProgress > 0 && uploadProgress < 100" class="mt-4">
            <div class="flex justify-between text-sm text-gray-600 mb-1">
              <span>Uploading and processing...</span>
              <span>{{ uploadProgress }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div class="bg-purple-600 h-2 rounded-full transition-all" :style="{ width: uploadProgress + '%' }"></div>
            </div>
          </div>
        </div>

        <div class="flex gap-4 mt-6">
          <button type="button" @click="closeAIModal"
            class="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300">
            Cancel
          </button>
          <button type="button" @click="generateWithAI" :disabled="aiLoading || (aiGenerationMode === 'pdf' && !uploadedPdf)"
            class="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 disabled:opacity-50">
            {{ aiLoading ? 'Generating...' : (autoCreateTest && aiGenerationMode === 'pdf' ? 'Generate & Create Test' : 'Generate Questions') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { backupAiService } from '../services/backupAiService'

const router = useRouter()

const form = ref({
  title: '',
  description: '',
  duration: 60,
  total_marks: 100,
  passing_marks: 40,
  enable_proctoring: true,
  enable_face_detection: true,
  enable_tab_switch_detection: true,
  enable_audio_monitoring: true,
  admission_mode: 'auto_admit',
  questions: []
})

const showAIModal = ref(false)
const aiGenerationMode = ref('topic') // 'topic' or 'pdf'
const uploadedPdf = ref(null)
const uploadProgress = ref(0)
const pdfDragOver = ref(false)
const autoCreateTest = ref(false) // Auto-create test after PDF question generation
const aiForm = ref({
  topic: '',
  num_questions: 5,
  difficulty: 'medium'
})
const loading = ref(false)
const aiLoading = ref(false)

const addQuestion = () => {
  form.value.questions.push({
    question_type: 'multiple_choice',
    text: '',
    optionsText: '',
    options: [],
    correct_answer: '',
    marks: 5
  })
}

const removeQuestion = (idx) => {
  form.value.questions.splice(idx, 1)
}

const handlePdfSelect = (event) => {
  const file = event.target.files[0]
  if (file && file.type === 'application/pdf') {
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB')
      return
    }
    uploadedPdf.value = file
  } else {
    alert('Please select a PDF file')
  }
}

const handlePdfDrop = (event) => {
  pdfDragOver.value = false
  const file = event.dataTransfer.files[0]
  if (file && file.type === 'application/pdf') {
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB')
      return
    }
    uploadedPdf.value = file
  } else {
    alert('Please drop a PDF file')
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
  autoCreateTest.value = false
}

const generateWithAI = async () => {
  aiLoading.value = true
  try {
    if (aiGenerationMode.value === 'pdf') {
      // PDF mode: Upload PDF and generate questions
      if (!uploadedPdf.value) {
        alert('Please upload a PDF file')
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
          
          form.value.questions.push({
            question_type: isTrueFalse ? 'true_false' : 'multiple_choice',
            text: q.question,
            optionsText: q.options ? q.options.join(', ') : (isTrueFalse ? 'True, False' : ''),
            options: q.options || (isTrueFalse ? ['True', 'False'] : []),
            correct_answer: q.correct_answer,
            marks: q.points || 5
          })
        })

        uploadProgress.value = 100
        
        // Auto-create test if checkbox is checked
        if (autoCreateTest.value) {
          closeAIModal()
          
          // Auto-fill test details if empty
          if (!form.value.title) {
            form.value.title = `Test from ${uploadedPdf.value.name.replace('.pdf', '')}`
          }
          if (!form.value.description) {
            form.value.description = `Auto-generated test with ${questionsResponse.data.questions.length} questions`
          }
          
          // Calculate total marks
          form.value.total_marks = form.value.questions.reduce((sum, q) => sum + q.marks, 0)
          form.value.passing_marks = Math.floor(form.value.total_marks * 0.4) // 40% passing
          
          // Submit the test immediately
          await handleSubmit()
          return
        }
      } catch (backendError) {
        console.error('Backend failed, trying fallback AI:', backendError)
        
        // Fallback: Use browser-based AI with PDF text extraction
        if (!backupAiService.isAvailable()) {
          throw new Error('Backend unavailable and no fallback AI configured. Please add VITE_GROQ_API_KEY to .env')
        }

        // Note: PDF text extraction in browser is limited
        // For production, use backend OCR service
        throw new Error('PDF processing requires backend server. Please ensure backend is running on port 8000. Error: ' + (backendError.response?.data?.detail || backendError.message))
      }
    } else {
      // Topic mode: Generate from text topic
      if (!aiForm.value.topic) {
        alert('Please enter a topic')
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
          form.value.questions.push({
            question_type: 'multiple_choice',
            text: q.question_text || q.question,
            optionsText: Array.isArray(q.options) ? q.options.join(', ') : Object.values(q.options).join(', '),
            options: Array.isArray(q.options) ? q.options : Object.values(q.options),
            correct_answer: q.correct_answer,
            marks: 5
          })
        })
      } catch (backendError) {
        console.error('Backend failed, trying fallback AI:', backendError)
        
        // Fallback: Use browser-based AI
        if (!backupAiService.isAvailable()) {
          throw new Error('Backend unavailable and no fallback AI configured. Please add VITE_GROQ_API_KEY to .env')
        }

        alert('Using fallback AI (backend unavailable)...')
        
        const questions = await backupAiService.generateQuestions(
          aiForm.value.topic,
          aiForm.value.num_questions,
          aiForm.value.difficulty
        )

        questions.forEach(q => {
          // Normalize question type
          const qType = q.type?.toLowerCase() || 'mcq'
          const isTrueFalse = qType.includes('true') || qType.includes('false') || qType === 'true_false'
          
          form.value.questions.push({
            question_type: isTrueFalse ? 'true_false' : 'multiple_choice',
            text: q.question,
            optionsText: q.options ? q.options.join(', ') : (isTrueFalse ? 'True, False' : ''),
            options: q.options || (isTrueFalse ? ['True', 'False'] : []),
            correct_answer: q.correct_answer,
            marks: q.points || 5
          })
        })
      }
    }

    closeAIModal()
  } catch (error) {
    console.error('Failed to generate questions:', error)
    alert('Failed to generate questions: ' + (error.response?.data?.detail || error.message))
    uploadProgress.value = 0
  } finally {
    aiLoading.value = false
  }
}

const handleSubmit = async () => {
  loading.value = true
  try {
    const questions = form.value.questions.map(q => ({
      question_type: q.question_type,
      text: q.text,
      options: q.optionsText ? q.optionsText.split(',').map(o => o.trim()) : [],
      correct_answer: q.correct_answer,
      marks: q.marks
    }))

    await api.post('/tests', {
      ...form.value,
      questions
    })

    router.push('/teacher/dashboard')
  } catch (error) {
    console.error('Failed to create test:', error)
    alert('Failed to create test. Please try again.')
  } finally {
    loading.value = false
  }
}
</script>
