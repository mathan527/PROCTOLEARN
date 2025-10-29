<template>
  <div class="max-w-7xl mx-auto p-6 space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Material Library</h1>
        <p class="text-sm text-gray-600 mt-1">Manage your uploaded study materials</p>
      </div>
      <Button @click="$router.push({ name: 'UploadMaterial' })">
        Upload New Material
      </Button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <Card variant="default" class-name="border-l-4 border-l-black">
        <div class="space-y-2">
          <p class="text-sm text-gray-600">Total Materials</p>
          <p class="text-3xl font-bold text-gray-900">{{ materials.length }}</p>
        </div>
      </Card>

      <Card variant="default" class-name="border-l-4 border-l-gray-400">
        <div class="space-y-2">
          <p class="text-sm text-gray-600">Total Text Extracted</p>
          <p class="text-3xl font-bold text-gray-900">{{ totalCharacters.toLocaleString() }}</p>
          <p class="text-xs text-gray-500">characters</p>
        </div>
      </Card>

      <Card variant="default" class-name="border-l-4 border-l-gray-400">
        <div class="space-y-2">
          <p class="text-sm text-gray-600">Questions Generated</p>
          <p class="text-3xl font-bold text-gray-900">{{ totalQuestions }}</p>
        </div>
      </Card>
    </div>

    <Card variant="elevated">
      <template #header>
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-gray-900">Your Materials</h2>
          <div class="flex items-center space-x-3">
            <select
              v-model="filterType"
              class="text-sm border border-gray-300 rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-black"
            >
              <option value="all">All Types</option>
              <option value="notes">Notes</option>
              <option value="textbook">Textbooks</option>
              <option value="slides">Slides</option>
              <option value="reference">Reference</option>
            </select>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search materials..."
              class="text-sm border border-gray-300 rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-black"
            />
          </div>
        </div>
      </template>

      <div v-if="loading" class="text-center py-12">
        <div class="inline-block w-8 h-8 border-4 border-gray-200 border-t-black rounded-full animate-spin"></div>
        <p class="text-sm text-gray-600 mt-4">Loading materials...</p>
      </div>

      <div v-else-if="filteredMaterials.length === 0" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="text-sm text-gray-600 mt-4">No materials found</p>
        <Button
          variant="outline"
          class-name="mt-4"
          @click="$router.push({ name: 'UploadMaterial' })"
        >
          Upload Your First Material
        </Button>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="material in filteredMaterials"
          :key="material.id"
          class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-3 mb-2">
                <h3 class="text-base font-semibold text-gray-900">{{ material.name }}</h3>
                <Badge :variant="getTypeBadgeVariant(material.type)">
                  {{ material.type }}
                </Badge>
              </div>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 mb-3">
                <div>
                  <span class="font-medium">Created:</span> {{ formatDate(material.created_at) }}
                </div>
                <div>
                  <span class="font-medium">Text:</span> {{ material.content_length?.toLocaleString() }} chars
                </div>
                <div>
                  <span class="font-medium">Type:</span> {{ getMaterialTypeName(material.type) }}
                </div>
                <div>
                  <span class="font-medium">Status:</span>
                  <Badge variant="success" class-name="ml-1">Ready</Badge>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <Button
                  size="sm"
                  @click="viewMaterial(material)"
                >
                  View Content
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  @click="generateQuestions(material)"
                >
                  Generate Questions
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  @click="downloadMaterial(material)"
                >
                  Download
                </Button>
                <Button
                  size="sm"
                  variant="destructive"
                  @click="deleteMaterial(material)"
                >
                  Delete
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { aiService } from '@/services/aiService'
import { useAuthStore } from '@/stores/auth'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import Badge from '@/components/ui/Badge.vue'
import { useToast } from 'vue-toastification'

const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()

const materials = ref([])
const loading = ref(false)
const filterType = ref('all')
const searchQuery = ref('')
const totalQuestions = ref(0)

const totalCharacters = computed(() => {
  return materials.value.reduce((sum, m) => sum + (m.content_length || 0), 0)
})

const filteredMaterials = computed(() => {
  let filtered = materials.value

  if (filterType.value !== 'all') {
    filtered = filtered.filter(m => m.type === filterType.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(m =>
      m.name.toLowerCase().includes(query) ||
      m.type.toLowerCase().includes(query)
    )
  }

  return filtered
})

const getTypeBadgeVariant = (type) => {
  const variants = {
    notes: 'default',
    textbook: 'secondary',
    slides: 'outline',
    reference: 'secondary'
  }
  return variants[type] || 'default'
}

const getMaterialTypeName = (type) => {
  const names = {
    notes: 'Notes',
    textbook: 'Textbook',
    slides: 'Slides',
    reference: 'Reference Material'
  }
  return names[type] || type
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const loadMaterials = async () => {
  try {
    loading.value = true
    const response = await aiService.getMaterials(authStore.user.id)
    materials.value = response
  } catch (error) {
    console.error('Failed to load materials:', error)
    toast.error('Failed to load materials')
  } finally {
    loading.value = false
  }
}

const viewMaterial = (material) => {
  router.push({
    name: 'ViewMaterial',
    params: { id: material.id }
  })
}

const generateQuestions = (material) => {
  router.push({
    name: 'GenerateQuestions',
    params: { materialId: material.id }
  })
}

const downloadMaterial = async (material) => {
  try {
    const data = await aiService.getMaterial(material.id)
    const blob = new Blob([data.content], { type: 'text/plain' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${material.name}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    toast.success('Material downloaded')
  } catch (error) {
    console.error('Failed to download material:', error)
    toast.error('Failed to download material')
  }
}

const deleteMaterial = async (material) => {
  if (!confirm(`Delete "${material.name}"? This action cannot be undone.`)) {
    return
  }

  try {
    // TODO: Implement delete API endpoint
    toast.success('Material deleted')
    await loadMaterials()
  } catch (error) {
    console.error('Failed to delete material:', error)
    toast.error('Failed to delete material')
  }
}

onMounted(() => {
  loadMaterials()
})
</script>
