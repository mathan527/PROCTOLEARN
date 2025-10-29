<template>
  <Card variant="elevated">
    <template #header>
      <h2 class="text-xl font-semibold text-gray-900">Upload Study Material</h2>
      <p class="text-sm text-gray-600 mt-1">Upload PDF or image files for OCR extraction and AI question generation</p>
    </template>

    <div class="space-y-6">
      <div>
        <label class="block text-sm font-medium text-gray-900 mb-2">
          Material Name
        </label>
        <Input
          v-model="materialName"
          placeholder="Enter material name"
          :disabled="uploading"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-900 mb-2">
          Material Type
        </label>
        <select
          v-model="materialType"
          :disabled="uploading"
          class="flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2"
        >
          <option value="notes">Notes</option>
          <option value="textbook">Textbook</option>
          <option value="slides">Slides</option>
          <option value="reference">Reference Material</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-900 mb-2">
          Upload File
        </label>
        <div
          @click="triggerFileInput"
          @dragover.prevent="dragOver = true"
          @dragleave.prevent="dragOver = false"
          @drop.prevent="handleFileDrop"
          :class="[
            'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
            dragOver ? 'border-black bg-gray-50' : 'border-gray-300 hover:border-gray-400'
          ]"
        >
          <input
            ref="fileInput"
            type="file"
            accept=".pdf,.png,.jpg,.jpeg"
            @change="handleFileSelect"
            class="hidden"
          />
          <div v-if="!selectedFile" class="space-y-2">
            <div class="text-gray-400">
              <svg class="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <div class="text-sm text-gray-600">
              <span class="font-semibold text-black">Click to upload</span> or drag and drop
            </div>
            <div class="text-xs text-gray-500">PDF, PNG, JPG or JPEG (max 10MB)</div>
          </div>
          <div v-else class="flex items-center justify-center space-x-3">
            <svg class="h-8 w-8 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <div class="text-left">
              <p class="text-sm font-medium text-gray-900">{{ selectedFile.name }}</p>
              <p class="text-xs text-gray-500">{{ formatFileSize(selectedFile.size) }}</p>
            </div>
            <button
              @click.stop="selectedFile = null"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div v-if="uploading" class="space-y-2">
        <div class="flex justify-between text-sm">
          <span class="text-gray-600">Uploading and processing...</span>
          <span class="font-medium text-gray-900">{{ uploadProgress }}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div
            class="bg-black h-2 rounded-full transition-all duration-300"
            :style="{ width: `${uploadProgress}%` }"
          ></div>
        </div>
      </div>

      <div v-if="extractedText" class="space-y-2">
        <div class="flex items-center justify-between">
          <label class="block text-sm font-medium text-gray-900">
            Extracted Text Preview
          </label>
          <Badge variant="success">Extraction Complete</Badge>
        </div>
        <div class="bg-gray-50 border border-gray-200 rounded-md p-4 max-h-40 overflow-y-auto">
          <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ extractedText.substring(0, 500) }}...</p>
        </div>
        <p class="text-xs text-gray-500">Total characters extracted: {{ extractedText.length }}</p>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-between items-center">
        <Button
          v-if="extractedText"
          variant="outline"
          @click="resetForm"
        >
          Upload Another
        </Button>
        <div v-else></div>
        <Button
          @click="uploadMaterial"
          :disabled="!canUpload || uploading"
        >
          {{ uploading ? 'Processing...' : extractedText ? 'Generate Questions' : 'Upload & Extract' }}
        </Button>
      </div>
    </template>
  </Card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { aiService } from '@/services/aiService'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Badge from '@/components/ui/Badge.vue'
import { useToast } from 'vue-toastification'

const router = useRouter()
const toast = useToast()

const materialName = ref('')
const materialType = ref('notes')
const selectedFile = ref(null)
const fileInput = ref(null)
const dragOver = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const extractedText = ref('')
const materialId = ref(null)

const canUpload = computed(() => {
  return materialName.value.trim() && selectedFile.value
})

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    validateAndSetFile(file)
  }
}

const handleFileDrop = (event) => {
  dragOver.value = false
  const file = event.dataTransfer.files[0]
  if (file) {
    validateAndSetFile(file)
  }
}

const validateAndSetFile = (file) => {
  const validTypes = ['application/pdf', 'image/png', 'image/jpeg']
  const maxSize = 10 * 1024 * 1024 // 10MB

  if (!validTypes.includes(file.type)) {
    toast.error('Invalid file type. Please upload PDF, PNG, or JPEG files.')
    return
  }

  if (file.size > maxSize) {
    toast.error('File size exceeds 10MB limit.')
    return
  }

  selectedFile.value = file
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const uploadMaterial = async () => {
  if (!canUpload.value) return

  if (extractedText.value && materialId.value) {
    router.push({
      name: 'GenerateQuestions',
      params: { materialId: materialId.value }
    })
    return
  }

  try {
    uploading.value = true
    uploadProgress.value = 30

    const result = await aiService.uploadMaterial(
      selectedFile.value,
      materialName.value,
      materialType.value
    )

    uploadProgress.value = 100
    extractedText.value = result.extracted_text
    materialId.value = result.material_id

    toast.success(`Successfully extracted ${result.text_length} characters`)
  } catch (error) {
    console.error('Upload failed:', error)
    toast.error(error.response?.data?.detail || 'Failed to upload and process material')
  } finally {
    uploading.value = false
  }
}

const resetForm = () => {
  materialName.value = ''
  materialType.value = 'notes'
  selectedFile.value = null
  extractedText.value = ''
  materialId.value = null
  uploadProgress.value = 0
}
</script>
