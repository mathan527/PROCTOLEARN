<template>
  <div :class="cn(cardVariants({ variant }), className)">
    <div v-if="$slots.header" class="border-b border-gray-200 px-6 py-4">
      <slot name="header" />
    </div>
    <div class="px-6 py-4">
      <slot />
    </div>
    <div v-if="$slots.footer" class="border-t border-gray-200 px-6 py-4">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
import { cardVariants, cn } from '@/lib/utils'

defineProps({
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'elevated'].includes(value)
  },
  className: {
    type: String,
    default: ''
  }
})
</script>
