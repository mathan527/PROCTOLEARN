import { defineStore } from "pinia"
import { ref } from "vue"

export const useQuizStore = defineStore("quiz", () => {
  const currentTest = ref(null)
  const currentQuestion = ref(0)
  const answers = ref({})
  const startTime = ref(null)
  const violations = ref([])

  const setTest = (test) => {
    currentTest.value = test
    currentQuestion.value = 0
    answers.value = {}
    startTime.value = Date.now()
    violations.value = []
  }

  const recordAnswer = (questionId, answer) => {
    answers.value[questionId] = answer
  }

  const recordViolation = (type, details) => {
    violations.value.push({
      type,
      details,
      timestamp: new Date(),
    })
  }

  const submitTest = () => {
    // TODO: Send answers and violations to backend
    const result = {
      testId: currentTest.value?.id,
      answers: answers.value,
      violations: violations.value,
      duration: Date.now() - startTime.value,
    }
    return result
  }

  return {
    currentTest,
    currentQuestion,
    answers,
    startTime,
    violations,
    setTest,
    recordAnswer,
    recordViolation,
    submitTest,
  }
})
