<template>
  <div 
    v-if="show" 
    class="fixed bottom-4 right-4 bg-white rounded-lg shadow-xl p-4 w-80 border-2"
    :class="statusColor"
  >
    <div class="flex items-center justify-between mb-3">
      <h3 class="font-bold text-gray-900">System Status</h3>
      <button @click="show = false" class="text-gray-400 hover:text-gray-600">✕</button>
    </div>
    
    <div v-if="loading" class="text-center py-4">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>
    
    <div v-else class="space-y-3">
      <!-- AI Generation Queue -->
      <div class="bg-gray-50 rounded-lg p-3">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-semibold text-gray-700">🤖 AI Generation</span>
          <span class="text-xs text-gray-500">
            {{ status.queues?.ai_generation?.available_slots || 0 }}/{{ status.queues?.ai_generation?.capacity || 3 }} available
          </span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div 
            class="bg-indigo-600 h-2 rounded-full transition-all"
            :style="{ width: getPercentage('ai_generation') + '%' }"
          ></div>
        </div>
        <div class="flex justify-between text-xs text-gray-500 mt-1">
          <span>Processing: {{ status.queues?.ai_generation?.processing || 0 }}</span>
          <span>Queued: {{ status.queues?.ai_generation?.queued || 0 }}</span>
        </div>
      </div>
      
      <!-- Test Processing -->
      <div class="bg-gray-50 rounded-lg p-3">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-semibold text-gray-700">📝 Test Processing</span>
          <span class="text-xs text-gray-500">
            {{ status.queues?.test_processing?.available_slots || 0 }}/{{ status.queues?.test_processing?.capacity || 10 }} available
          </span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div 
            class="bg-green-600 h-2 rounded-full transition-all"
            :style="{ width: getPercentage('test_processing') + '%' }"
          ></div>
        </div>
        <div class="flex justify-between text-xs text-gray-500 mt-1">
          <span>Processing: {{ status.queues?.test_processing?.processing || 0 }}</span>
          <span>Queued: {{ status.queues?.test_processing?.queued || 0 }}</span>
        </div>
      </div>
      
      <!-- Proctoring -->
      <div class="bg-gray-50 rounded-lg p-3">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-semibold text-gray-700">🎥 Proctoring</span>
          <span class="text-xs text-gray-500">
            {{ status.queues?.proctoring?.available_slots || 0 }}/{{ status.queues?.proctoring?.capacity || 50 }} available
          </span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div 
            class="bg-purple-600 h-2 rounded-full transition-all"
            :style="{ width: getPercentage('proctoring') + '%' }"
          ></div>
        </div>
        <div class="flex justify-between text-xs text-gray-500 mt-1">
          <span>Active: {{ status.queues?.proctoring?.processing || 0 }}</span>
          <span>Queued: {{ status.queues?.proctoring?.queued || 0 }}</span>
        </div>
      </div>
      
      <!-- Overall Status -->
      <div class="text-center pt-2 border-t">
        <span 
          class="inline-block px-3 py-1 rounded-full text-xs font-semibold"
          :class="status.system_status === 'operational' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'"
        >
          {{ status.system_status === 'operational' ? '✓ System Operational' : '⚠ System Busy' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '../api'

const show = ref(true)
const loading = ref(false)
const status = ref({})
let intervalId = null

const statusColor = computed(() => {
  if (status.value.system_status === 'operational') {
    return 'border-green-500'
  }
  return 'border-yellow-500'
})

const getPercentage = (queueName) => {
  const queue = status.value.queues?.[queueName]
  if (!queue || !queue.capacity) return 0
  return Math.min(100, (queue.processing / queue.capacity) * 100)
}

const fetchStatus = async () => {
  try {
    const response = await api.get('/queue/status')
    status.value = response.data
  } catch (error) {
    console.error('Failed to fetch queue status:', error)
  }
}

onMounted(() => {
  fetchStatus()
  // Update every 5 seconds
  intervalId = setInterval(fetchStatus, 5000)
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})
</script>
