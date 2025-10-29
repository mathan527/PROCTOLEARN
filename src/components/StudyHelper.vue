<template>
  <div class="max-w-4xl mx-auto p-6 space-y-6">
    <Card variant="elevated">
      <template #header>
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-semibold text-gray-900">AI Study Assistant</h2>
            <p class="text-sm text-gray-600 mt-1">Get instant help with your studies powered by AI</p>
          </div>
          <Badge variant="default">AI Powered</Badge>
        </div>
      </template>

      <div class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-900 mb-2">
            What do you need help with?
          </label>
          <textarea
            v-model="question"
            placeholder="Ask any question about your study material..."
            rows="4"
            :disabled="loading"
            class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
          ></textarea>
          <p class="text-xs text-gray-500 mt-1">Be specific for better results</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-900 mb-2">
            Additional Context (Optional)
          </label>
          <textarea
            v-model="context"
            placeholder="Provide any additional context or specific topic you're studying..."
            rows="3"
            :disabled="loading"
            class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
          ></textarea>
        </div>

        <Button
          @click="getHelp"
          :disabled="!question.trim() || loading"
          class="w-full"
        >
          {{ loading ? 'Getting Answer...' : 'Get AI Help' }}
        </Button>

        <div v-if="loading" class="space-y-2">
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">AI is thinking...</span>
            <Badge variant="default">Processing</Badge>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div class="bg-black h-2 rounded-full animate-pulse w-full"></div>
          </div>
        </div>

        <div v-if="answer" class="space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-medium text-gray-900">AI Answer</h3>
            <Badge variant="success">Answer Ready</Badge>
          </div>
          <Card variant="default" class-name="bg-gray-50">
            <div class="prose prose-sm max-w-none">
              <div v-html="formattedAnswer" class="text-gray-700"></div>
            </div>
          </Card>
          <div class="flex items-center justify-end space-x-2">
            <Button
              variant="outline"
              size="sm"
              @click="copyAnswer"
            >
              Copy Answer
            </Button>
            <Button
              variant="outline"
              size="sm"
              @click="askFollowUp"
            >
              Ask Follow-up
            </Button>
          </div>
        </div>
      </div>
    </Card>

    <Card v-if="recentQuestions.length > 0" variant="default">
      <template #header>
        <h3 class="text-lg font-semibold text-gray-900">Recent Questions</h3>
      </template>

      <div class="space-y-3">
        <button
          v-for="(item, index) in recentQuestions"
          :key="index"
          @click="loadQuestion(item)"
          class="w-full text-left p-4 border border-gray-200 rounded-md hover:bg-gray-50 transition-colors"
        >
          <p class="text-sm font-medium text-gray-900 mb-1">{{ item.question }}</p>
          <p class="text-xs text-gray-500">{{ formatDate(item.timestamp) }}</p>
        </button>
      </div>
    </Card>

    <Card variant="default">
      <template #header>
        <h3 class="text-lg font-semibold text-gray-900">Study Tips</h3>
      </template>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="space-y-2">
          <h4 class="text-sm font-medium text-gray-900">Effective Questions</h4>
          <ul class="text-sm text-gray-600 space-y-1 list-disc list-inside">
            <li>Be specific about the topic</li>
            <li>Include relevant context</li>
            <li>Ask one thing at a time</li>
            <li>Clarify what you don't understand</li>
          </ul>
        </div>
        <div class="space-y-2">
          <h4 class="text-sm font-medium text-gray-900">Best Practices</h4>
          <ul class="text-sm text-gray-600 space-y-1 list-disc list-inside">
            <li>Review the answer carefully</li>
            <li>Try to understand, not memorize</li>
            <li>Ask follow-up questions</li>
            <li>Practice with examples</li>
          </ul>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { marked } from 'marked'
import { aiService } from '@/services/aiService'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import Badge from '@/components/ui/Badge.vue'
import { useToast } from 'vue-toastification'

const toast = useToast()

const question = ref('')
const context = ref('')
const answer = ref('')
const loading = ref(false)
const recentQuestions = ref([])

const formattedAnswer = computed(() => {
  if (!answer.value) return ''
  return marked(answer.value)
})

const getHelp = async () => {
  if (!question.value.trim()) return

  try {
    loading.value = true

    const response = await aiService.getStudyHelp(
      question.value,
      context.value
    )

    answer.value = response

    // Save to recent questions
    recentQuestions.value.unshift({
      question: question.value,
      context: context.value,
      answer: response,
      timestamp: new Date()
    })

    // Keep only last 5 questions
    if (recentQuestions.value.length > 5) {
      recentQuestions.value = recentQuestions.value.slice(0, 5)
    }

    // Save to localStorage
    localStorage.setItem('recentStudyQuestions', JSON.stringify(recentQuestions.value))

    toast.success('Answer received!')
  } catch (error) {
    console.error('Failed to get study help:', error)
    toast.error(error.response?.data?.detail || 'Failed to get AI help')
  } finally {
    loading.value = false
  }
}

const copyAnswer = async () => {
  try {
    await navigator.clipboard.writeText(answer.value)
    toast.success('Answer copied to clipboard')
  } catch (error) {
    toast.error('Failed to copy answer')
  }
}

const askFollowUp = () => {
  context.value = `Previous question: ${question.value}\nPrevious answer: ${answer.value}`
  question.value = ''
  answer.value = ''
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const loadQuestion = (item) => {
  question.value = item.question
  context.value = item.context
  answer.value = item.answer
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const formatDate = (date) => {
  const now = new Date()
  const diff = now - new Date(date)
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
  if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`
  return `${days} day${days > 1 ? 's' : ''} ago`
}

// Load recent questions from localStorage
const loadRecentQuestions = () => {
  try {
    const stored = localStorage.getItem('recentStudyQuestions')
    if (stored) {
      recentQuestions.value = JSON.parse(stored)
    }
  } catch (error) {
    console.error('Failed to load recent questions:', error)
  }
}

loadRecentQuestions()
</script>
