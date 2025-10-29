import { api } from '../api'
import { backupAiService } from './backupAiService'

export const aiService = {
  async uploadMaterial(file, materialName, materialType = 'notes', teacherId) {
    // File uploads MUST go through backend (OCR processing required)
    const formData = new FormData()
    formData.append('file', file)
    formData.append('material_name', materialName)
    formData.append('material_type', materialType)
    
    const { data } = await api.post('/ai-materials/upload-material', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return data
  },

  async generateQuestions(materialId, options = {}) {
    const {
      numQuestions = 10,
      difficulty = 'medium',
      questionTypes = ['multiple_choice', 'true_false'],
      testId = null
    } = options

    try {
      const { data } = await api.post('/ai-materials/generate-questions', {
        material_id: materialId,
        num_questions: numQuestions,
        difficulty,
        question_types: questionTypes,
        test_id: testId
      })
      return data
    } catch (error) {
      // Backup: Try generating questions with direct AI
      if (backupAiService.isAvailable()) {
        console.warn('⚠️ Backend question generation failed, using backup AI:', error.message)
        
        // Try to get material content first (will fail if backend completely down)
        try {
          const material = await this.getMaterial(materialId)
          const questions = await backupAiService.generateQuestions(
            material.content,
            numQuestions,
            difficulty
          )
          return { questions, status: 'generated_offline' }
        } catch (materialError) {
          console.error('Cannot get material for offline generation:', materialError)
          throw error
        }
      }
      throw error
    }
  },

  async getMaterials(teacherId) {
    // Materials MUST come from database (no offline storage yet)
    const { data } = await api.get(`/ai-materials/materials/${teacherId}`)
    return data
  },

  async getMaterial(materialId) {
    // Material content MUST come from database
    const { data } = await api.get(`/ai-materials/material/${materialId}`)
    return data
  },

  async getStudyHelp(question, context = '', studentId = null) {
    console.log('🔵 Calling study-help API:', {
      endpoint: '/ai-materials/study-help',
      question,
      contextLength: context.length,
      studentId,
      backupAvailable: backupAiService.isAvailable()
    })
    
    try {
      // Primary: Backend API (saves to database)
      const { data } = await api.post('/ai-materials/study-help', {
        question,
        context,
        student_id: studentId
      })
      
      console.log('✅ Study-help response from backend:', data)
      return data.explanation || data.answer
      
    } catch (error) {
      console.error('❌ Backend study-help failed:', error)
      
      // Fallback: Use direct Groq AI (won't save to database)
      if (backupAiService.isAvailable()) {
        console.warn('⚠️ Using backup AI service (answer won\'t be saved to history)')
        
        try {
          const answer = await backupAiService.getStudyHelp(question, context)
          console.log('✅ Got answer from backup AI')
          return answer
        } catch (backupError) {
          console.error('❌ Backup AI also failed:', backupError)
          throw new Error('AI service unavailable. Please check your connection and try again.')
        }
      }
      
      throw error
    }
  },

  async getSummary(materialId, pages = null) {
    console.log('🔵 Calling summary API:', { materialId, pages })
    
    try {
      // Primary: Backend API
      const { data } = await api.post('/ai-materials/summarize', {
        material_id: materialId,
        pages
      })
      
      console.log('✅ Summary from backend')
      return data.summary
      
    } catch (error) {
      console.error('❌ Backend summary failed:', error)
      
      // Fallback: Get material and use direct AI
      if (backupAiService.isAvailable()) {
        console.warn('⚠️ Using backup AI for summary')
        
        try {
          const material = await this.getMaterial(materialId)
          const summary = await backupAiService.getSummary(material.content, pages)
          console.log('✅ Got summary from backup AI')
          return summary
        } catch (backupError) {
          console.error('❌ Backup summary also failed:', backupError)
          throw new Error('Summary service unavailable.')
        }
      }
      
      throw error
    }
  },

  async deleteMaterial(materialId) {
    const { data } = await api.delete(`/ai-materials/material/${materialId}`)
    return data
  }
}
