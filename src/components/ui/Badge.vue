<template>
  <span :class="cn(badgeVariants({ variant }), className)">
    <slot />
  </span>
</template>

<script setup>
import { badgeVariants, cn } from '@/lib/utils'

defineProps({
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'secondary', 'destructive', 'outline', 'success', 'warning'].includes(value)
  },
  className: {
    type: String,
    default: ''
  }
})
</script>
