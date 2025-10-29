<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-8 py-6">
        <h1 class="text-3xl font-bold text-gray-900">AI Question Generator</h1>
        <p class="text-gray-600 mt-2">Upload PDFs and generate test questions with DeepSeek OCR + AI</p>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-8 py-12">
      <!-- Step 1: Upload PDFs -->
      <section class="bg-white rounded-xl shadow-lg p-8 mb-8">
        <h2 class="text-2xl font-bold mb-6 flex items-center gap-2">
          <span>📄</span> Step 1: Upload Teaching Materials
        </h2>
        
        <div class="border-2 border-dashed border-gray-300 rounded-xl p-12 text-center hover:border-blue-500 transition"
          @dragover.prevent="dragOver = true"
          @dragleave.prevent="dragOver = false"
          @drop.prevent="handleDrop"
          :class="dragOver ? 'border-blue-500 bg-blue-50' : ''">
          <input type="file" ref="fileInput" @change="handleFileSelect" accept=".pdf" multiple class="hidden" />
          <div class="text-6xl mb-4">📚</div>
          <p class="text-xl font-semibold mb-2">Drop PDF files here or click to browse</p>
          <p class="text-gray-600 mb-4">Supports: Textbooks, lecture notes, worksheets, previous exams</p>
          <button @click="$refs.fileInput.click()" class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold">
            Choose Files
          </button>
        </div>

        <!-- Uploaded Files List -->
        <div v-if="uploadedFiles.length > 0" class="mt-6 space-y-3">
          <h3 class="font-semibold text-gray-700">Uploaded Files ({{ uploadedFiles.length }})</h3>
          <div v-for="(file, idx) in uploadedFiles" :key="idx" 
            class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div class="flex items-center gap-3">
              <span class="text-2xl">📄</span>
              <div>
                <p class="font-semibold">{{ file.name }}</p>
                <p class="text-sm text-gray-600">{{ (file.size / 1024 / 1024).toFixed(2) }} MB</p>
              </div>
            </div>
            <button @click="removeFile(idx)" class="text-red-600 hover:text-red-800">
              <span class="text-xl">×</span>
            </button>
          </div>
        </div>

        <button v-if="uploadedFiles.length > 0 && !processing" 
          @click="processFiles"
          class="mt-6 w-full py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 font-bold text-lg">
          🔍 Process with DeepSeek OCR
        </button>

        <!-- Processing Status -->
        <div v-if="processing" class="mt-6 p-6 bg-blue-50 rounded-lg">
          <div class="flex items-center gap-3 mb-4">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p class="text-lg font-semibold text-blue-900">Processing PDFs...</p>
          </div>
          <div class="space-y-2">
            <div v-for="status in processingStatus" :key="status.file" class="text-sm">
              <span class="font-semibold">{{ status.file }}:</span>
              <span class="ml-2" :class="status.status === 'done' ? 'text-green-600' : 'text-blue-600'">
                {{ status.message }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- Step 2: Configure Question Generation -->
      <section v-if="extractedContent" class="bg-white rounded-xl shadow-lg p-8 mb-8">
        <h2 class="text-2xl font-bold mb-6 flex items-center gap-2">
          <span>⚙️</span> Step 2: Configure Question Generation
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label class="block text-sm font-semibold mb-2">Number of Questions</label>
            <input v-model.number="config.questionCount" type="number" min="5" max="100" 
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200" />
          </div>

          <div>
            <label class="block text-sm font-semibold mb-2">Difficulty Level</label>
            <select v-model="config.difficulty" 
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200">
              <option value="easy">Easy - Basic recall</option>
              <option value="medium">Medium - Application</option>
              <option value="hard">Hard - Analysis & synthesis</option>
              <option value="mixed">Mixed - All levels</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-semibold mb-2">Question Types</label>
            <div class="space-y-2">
              <label class="flex items-center gap-2">
                <input type="checkbox" v-model="config.types.multipleChoice" class="w-4 h-4" />
                <span>Multiple Choice</span>
              </label>
              <label class="flex items-center gap-2">
                <input type="checkbox" v-model="config.types.trueFalse" class="w-4 h-4" />
                <span>True/False</span>
              </label>
              <label class="flex items-center gap-2">
                <input type="checkbox" v-model="config.types.shortAnswer" class="w-4 h-4" />
                <span>Short Answer</span>
              </label>
            </div>
          </div>

          <div>
            <label class="block text-sm font-semibold mb-2">Focus Areas (optional)</label>
            <textarea v-model="config.focusAreas" rows="4" 
              placeholder="e.g., Chapter 3: Calculus, Derivatives, Integration..."
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200"></textarea>
          </div>
        </div>

        <div class="mb-6">
          <label class="block text-sm font-semibold mb-2">Custom Instructions (optional)</label>
          <textarea v-model="config.customPrompt" rows="3" 
            placeholder="e.g., Focus on practical applications, include diagrams, test problem-solving skills..."
            class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200"></textarea>
        </div>

        <button @click="generateQuestions" :disabled="generating"
          class="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 font-bold text-lg disabled:opacity-50">
          {{ generating ? '🤖 Generating Questions...' : '✨ Generate Questions with AI' }}
        </button>
      </section>

      <!-- Step 3: Review Generated Questions -->
      <section v-if="generatedQuestions.length > 0" class="bg-white rounded-xl shadow-lg p-8">
        <h2 class="text-2xl font-bold mb-6 flex items-center gap-2">
          <span>✅</span> Step 3: Review & Edit Questions
        </h2>

        <div class="mb-6 p-4 bg-green-50 rounded-lg border border-green-200">
          <p class="text-green-800 font-semibold">
            ✓ Generated {{ generatedQuestions.length }} questions successfully!
          </p>
        </div>

        <div class="space-y-6 mb-8">
          <div v-for="(q, idx) in generatedQuestions" :key="idx" class="border-2 border-gray-200 rounded-lg p-6 hover:border-blue-300 transition">
            <div class="flex justify-between items-start mb-4">
              <div class="flex items-center gap-3">
                <span class="text-2xl font-bold text-blue-600">{{ idx + 1 }}</span>
                <span class="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-semibold">
                  {{ q.type }}
                </span>
                <span class="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm font-semibold">
                  {{ q.difficulty }}
                </span>
              </div>
              <button @click="removeQuestion(idx)" class="text-red-600 hover:text-red-800 font-bold">
                Remove
              </button>
            </div>

            <div class="mb-4">
              <label class="block text-sm font-semibold mb-2">Question Text</label>
              <textarea v-model="q.text" rows="3" 
                class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500"></textarea>
            </div>

            <div v-if="q.type === 'multiple_choice' && q.options" class="mb-4">
              <label class="block text-sm font-semibold mb-2">Options</label>
              <div class="space-y-2">
                <input v-for="(opt, optIdx) in q.options" :key="optIdx" v-model="q.options[optIdx]"
                  class="w-full px-4 py-2 border-2 border-gray-300 rounded-lg" />
              </div>
            </div>

            <div class="mb-4">
              <label class="block text-sm font-semibold mb-2">Correct Answer</label>
              <input v-model="q.correctAnswer" 
                class="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-green-500" />
            </div>

            <div v-if="q.explanation" class="p-3 bg-blue-50 rounded-lg">
              <p class="text-sm text-blue-900"><strong>AI Explanation:</strong> {{ q.explanation }}</p>
            </div>
          </div>
        </div>

        <div class="flex gap-4">
          <button @click="createTest" 
            class="flex-1 py-4 bg-green-600 text-white rounded-lg hover:bg-green-700 font-bold text-lg">
            📝 Create Test from Questions
          </button>
          <button @click="downloadQuestions" 
            class="px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-bold">
            💾 Download JSON
          </button>
        </div>
      </section>

      <!-- Extracted Content Preview (Debug) -->
      <section v-if="extractedContent && showDebug" class="bg-gray-900 text-green-400 rounded-xl p-6 font-mono text-sm overflow-auto max-h-96">
        <h3 class="text-white font-bold mb-4">Extracted Content (Debug)</h3>
        <pre>{{ extractedContent }}</pre>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()

const fileInput = ref(null)
const uploadedFiles = ref([])
const dragOver = ref(false)
const processing = ref(false)
const processingStatus = ref([])
const extractedContent = ref(null)
const generating = ref(false)
const generatedQuestions = ref([])
const showDebug = ref(false)

const config = ref({
  questionCount: 20,
  difficulty: 'mixed',
  types: {
    multipleChoice: true,
    trueFalse: true,
    shortAnswer: false
  },
  focusAreas: '',
  customPrompt: ''
})

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  uploadedFiles.value.push(...files)
}

const handleDrop = (event) => {
  dragOver.value = false
  const files = Array.from(event.dataTransfer.files).filter(f => f.type === 'application/pdf')
  uploadedFiles.value.push(...files)
}

const removeFile = (idx) => {
  uploadedFiles.value.splice(idx, 1)
}

const processFiles = async () => {
  processing.value = true
  processingStatus.value = []
  
  try {
    // Upload PDFs and process with DeepSeek OCR
    const formData = new FormData()
    uploadedFiles.value.forEach((file, idx) => {
      formData.append('files', file)
      processingStatus.value.push({ file: file.name, status: 'processing', message: 'Uploading...' })
    })
    
    // Call backend API to process with DeepSeek OCR
    const response = await api.post('/ai/process-pdfs', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        const percent = Math.round((e.loaded * 100) / e.total)
        processingStatus.value[0].message = `Uploading... ${percent}%`
      }
    })
    
    extractedContent.value = response.data.content
    
    processingStatus.value.forEach(s => {
      s.status = 'done'
      s.message = '✓ Extracted text, equations, and diagrams'
    })
    
  } catch (error) {
    console.error('Processing failed:', error)
    alert('Failed to process PDFs: ' + (error.response?.data?.detail || error.message))
  } finally {
    processing.value = false
  }
}

const generateQuestions = async () => {
  generating.value = true
  
  try {
    const types = []
    if (config.value.types.multipleChoice) types.push('multiple_choice')
    if (config.value.types.trueFalse) types.push('true_false')
    if (config.value.types.shortAnswer) types.push('short_answer')
    
    const response = await api.post('/ai/generate-questions', {
      content: extractedContent.value,
      question_count: config.value.questionCount,
      difficulty: config.value.difficulty,
      question_types: types,
      focus_areas: config.value.focusAreas,
      custom_prompt: config.value.customPrompt
    })
    
    generatedQuestions.value = response.data.questions
    
  } catch (error) {
    console.error('Generation failed:', error)
    alert('Failed to generate questions: ' + (error.response?.data?.detail || error.message))
  } finally {
    generating.value = false
  }
}

const removeQuestion = (idx) => {
  generatedQuestions.value.splice(idx, 1)
}

const createTest = () => {
  // Store questions in sessionStorage and navigate to test creation
  sessionStorage.setItem('aiGeneratedQuestions', JSON.stringify(generatedQuestions.value))
  router.push('/teacher/test-creation?fromAI=true')
}

const downloadQuestions = () => {
  const blob = new Blob([JSON.stringify(generatedQuestions.value, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `ai_questions_${new Date().toISOString().split('T')[0]}.json`
  link.click()
}
</script>
