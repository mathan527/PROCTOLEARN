<template>
  <Card variant="elevated">
    <template #header>
      <h2 class="text-xl font-semibold text-gray-900">Generate AI Questions</h2>
      <p class="text-sm text-gray-600 mt-1">Configure and generate questions from extracted material</p>
    </template>

    <div class="space-y-6">
      <div class="bg-gray-50 border border-gray-200 rounded-md p-4">
        <h3 class="text-sm font-medium text-gray-900 mb-2">Material Information</h3>
        <div class="text-sm space-y-1">
          <p class="text-gray-700"><span class="font-medium">Name:</span> {{ material?.name }}</p>
          <p class="text-gray-700"><span class="font-medium">Type:</span> {{ material?.type }}</p>
          <p class="text-gray-700"><span class="font-medium">Content Length:</span> {{ material?.content_length }} characters</p>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-900 mb-2">
          Number of Questions
        </label>
        <Input
          v-model.number="numQuestions"
          type="number"
          min="1"
          max="50"
          :disabled="generating"
        />
        <p class="text-xs text-gray-500 mt-1">Generate between 1 and 50 questions</p>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-900 mb-2">
          Difficulty Level
        </label>
        <div class="grid grid-cols-3 gap-3">
          <button
            v-for="level in ['easy', 'medium', 'hard']"
            :key="level"
            @click="difficulty = level"
            :class="[
              'px-4 py-2 text-sm font-medium rounded-md border transition-colors',
              difficulty === level
                ? 'bg-black text-white border-black'
                : 'bg-white text-gray-700 border-gray-300 hover:border-gray-400'
            ]"
            :disabled="generating"
          >
            {{ level.charAt(0).toUpperCase() + level.slice(1) }}
          </button>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-900 mb-2">
          Question Types
        </label>
        <div class="space-y-2">
          <label
            v-for="type in questionTypes"
            :key="type.value"
            class="flex items-center space-x-3 p-3 border border-gray-200 rounded-md hover:bg-gray-50 cursor-pointer"
          >
            <input
              type="checkbox"
              v-model="selectedTypes"
              :value="type.value"
              :disabled="generating"
              class="h-4 w-4 rounded border-gray-300 text-black focus:ring-black"
            />
            <div class="flex-1">
              <p class="text-sm font-medium text-gray-900">{{ type.label }}</p>
              <p class="text-xs text-gray-500">{{ type.description }}</p>
            </div>
          </label>
        </div>
      </div>

      <div v-if="generating" class="space-y-2">
        <div class="flex justify-between text-sm">
          <span class="text-gray-600">Generating questions with AI...</span>
          <Badge variant="default">Processing</Badge>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div class="bg-black h-2 rounded-full animate-pulse w-full"></div>
        </div>
      </div>

      <div v-if="generatedQuestions.length > 0" class="space-y-3">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-medium text-gray-900">Generated Questions Preview</h3>
          <Badge variant="success">{{ generatedQuestions.length }} Questions</Badge>
        </div>
        <div class="space-y-3 max-h-96 overflow-y-auto">
          <div
            v-for="(question, index) in generatedQuestions"
            :key="index"
            class="border border-gray-200 rounded-md p-4 bg-white"
          >
            <div class="flex items-start justify-between mb-2">
              <h4 class="text-sm font-medium text-gray-900">Question {{ index + 1 }}</h4>
              <Badge variant="secondary">{{ question.type }}</Badge>
            </div>
            <p class="text-sm text-gray-700 mb-3">{{ question.question }}</p>
            <div v-if="question.options" class="space-y-1">
              <p
                v-for="(option, optIndex) in question.options"
                :key="optIndex"
                :class="[
                  'text-sm px-3 py-1.5 rounded',
                  option === question.correct_answer
                    ? 'bg-green-50 text-green-900 font-medium'
                    : 'bg-gray-50 text-gray-700'
                ]"
              >
                {{ String.fromCharCode(65 + optIndex) }}. {{ option }}
              </p>
            </div>
            <p v-else class="text-sm text-gray-600">
              <span class="font-medium">Answer:</span> {{ question.correct_answer }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-between items-center">
        <Button
          variant="outline"
          @click="$router.back()"
          :disabled="generating"
        >
          Back
        </Button>
        <Button
          @click="generateQuestions"
          :disabled="!canGenerate || generating"
        >
          {{ generating ? 'Generating...' : generatedQuestions.length > 0 ? 'Add to Test' : 'Generate Questions' }}
        </Button>
      </div>
    </template>
  </Card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { aiService } from '@/services/aiService'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Badge from '@/components/ui/Badge.vue'
import { useToast } from 'vue-toastification'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const material = ref(null)
const numQuestions = ref(10)
const difficulty = ref('medium')
const selectedTypes = ref(['multiple_choice', 'true_false'])
const generating = ref(false)
const generatedQuestions = ref([])

const questionTypes = [
  {
    value: 'multiple_choice',
    label: 'Multiple Choice',
    description: 'Questions with 4 answer options'
  },
  {
    value: 'true_false',
    label: 'True/False',
    description: 'Binary true or false questions'
  },
  {
    value: 'short_answer',
    label: 'Short Answer',
    description: 'Brief text-based answers'
  }
]

const canGenerate = computed(() => {
  return numQuestions.value > 0 && numQuestions.value <= 50 && selectedTypes.value.length > 0
})

onMounted(async () => {
  const materialId = route.params.materialId
  if (materialId) {
    try {
      material.value = await aiService.getMaterial(materialId)
    } catch (error) {
      console.error('Failed to load material:', error)
      toast.error('Failed to load material')
      router.back()
    }
  }
})

const generateQuestions = async () => {
  if (!canGenerate.value) return

  if (generatedQuestions.value.length > 0) {
    // Navigate to test creation with generated questions
    router.push({
      name: 'TestCreation',
      state: { generatedQuestions: generatedQuestions.value }
    })
    return
  }

  try {
    generating.value = true

    const result = await aiService.generateQuestions(route.params.materialId, {
      numQuestions: numQuestions.value,
      difficulty: difficulty.value,
      questionTypes: selectedTypes.value,
      testId: route.query.testId || null
    })

    generatedQuestions.value = result.questions
    toast.success(`Successfully generated ${result.count} questions`)

    if (route.query.testId) {
      toast.success('Questions added to test')
      router.push({ name: 'TestCreation', params: { id: route.query.testId } })
    }
  } catch (error) {
    console.error('Generation failed:', error)
    toast.error(error.response?.data?.detail || 'Failed to generate questions')
  } finally {
    generating.value = false
  }
}
</script>
