import { defineStore } from "pinia"
import { ref } from "vue"

export const useProctoringStore = defineStore("proctoring", () => {
  const activeSessions = ref([])
  const alerts = ref([])
  const studentFeeds = ref({})

  const addSession = (session) => {
    activeSessions.value.push(session)
  }

  const recordAlert = (studentId, alertType, details) => {
    alerts.value.push({
      studentId,
      alertType,
      details,
      timestamp: new Date(),
    })
  }

  const updateStudentFeed = (studentId, feedData) => {
    studentFeeds.value[studentId] = feedData
  }

  return {
    activeSessions,
    alerts,
    studentFeeds,
    addSession,
    recordAlert,
    updateStudentFeed,
  }
})
