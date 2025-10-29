<template>
  <div v-if="visible" :class="type === 'error' ? 'bg-red-500' : 'bg-green-500'" class="fixed bottom-4 right-4 text-white px-6 py-3 rounded-lg shadow-lg">
    {{ message }}
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  message: String,
  type: { type: String, default: 'success' },
  duration: { type: Number, default: 3000 }
})

const visible = ref(true)

setTimeout(() => {
  visible.value = false
}, props.duration)
</script>
