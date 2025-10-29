import Groq from 'groq-sdk'

// Browser-compatible backup AI service using Groq directly
class BackupAiService {
  constructor() {
    this.groqApiKey = import.meta.env.VITE_GROQ_API_KEY
    this.client = null
    this.initializeClient()
  }

  initializeClient() {
    if (this.groqApiKey) {
      try {
        this.client = new Groq({
          apiKey: this.groqApiKey,
          dangerouslyAllowBrowser: true // Enable browser usage
        })
        console.log('✅ Backup Groq AI client initialized')
      } catch (error) {
        console.error('❌ Failed to initialize Groq client:', error)
      }
    } else {
      console.warn('⚠️ GROQ_API_KEY not found - backup AI service disabled')
    }
  }

  isAvailable() {
    return !!this.client
  }

  async getStudyHelp(question, context = '') {
    if (!this.client) {
      throw new Error('Backup AI service not available - missing API key')
    }

    const prompt = `You are a helpful tutor. A student needs help with the following:

Question: ${question}

${context ? `Context: ${context.substring(0, 2000)}` : ''}

Provide:
1. A clear explanation
2. Step-by-step breakdown if applicable
3. Key concepts to understand
4. Related topics to study

Keep your response concise but thorough.`

    try {
      const response = await this.client.chat.completions.create({
        model: 'llama-3.3-70b-versatile',
        messages: [
          {
            role: 'system',
            content: 'You are a patient, knowledgeable tutor who explains concepts clearly and encourages learning.'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.8,
        max_tokens: 1500
      })

      return response.choices[0].message.content
    } catch (error) {
      console.error('Backup AI service error:', error)
      throw error
    }
  }

  async generateQuestions(textContent, numQuestions = 5, difficulty = 'medium') {
    if (!this.client) {
      throw new Error('Backup AI service not available - missing API key')
    }

    const questionTypes = ['multiple_choice', 'true_false']
    
    // Truncate content more aggressively to avoid token limits
    const truncatedContent = textContent.substring(0, 2000)
    
    const prompt = `Generate ${numQuestions} exam questions based on this content.

Content:
${truncatedContent}

Requirements:
- Difficulty: ${difficulty}
- Question types: multiple choice and true/false
- Test understanding, not memorization
- For MCQ: 4 options with one correct answer
- For True/False: include explanation

Return ONLY valid JSON array:
[
  {
    "question": "Question text",
    "type": "mcq",
    "options": ["A", "B", "C", "D"],
    "correct_answer": "B",
    "explanation": "Why this is correct",
    "points": 2
  }
]`

    try {
      const response = await this.client.chat.completions.create({
        model: 'llama-3.3-70b-versatile',
        messages: [
          {
            role: 'system',
            content: 'You are an expert educator. Return only valid JSON arrays.'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.7,
        max_tokens: 2000,  // Reduced to prevent incomplete JSON
        response_format: { type: 'json_object' }
      })

      const content = response.choices[0].message.content
      
      try {
        const result = JSON.parse(content)
        return result.questions || [result]
      } catch (e) {
        // Try to extract JSON array
        const start = content.indexOf('[')
        const end = content.lastIndexOf(']') + 1
        if (start !== -1 && end !== 0) {
          return JSON.parse(content.substring(start, end))
        }
        throw new Error('Failed to parse AI response')
      }
    } catch (error) {
      console.error('Backup question generation error:', error)
      throw error
    }
  }

  async getSummary(content, pages = null) {
    if (!this.client) {
      throw new Error('Backup AI service not available - missing API key')
    }

    const pageInfo = pages ? `Pages ${pages.start}-${pages.end}` : 'Full document'
    const prompt = `Provide a comprehensive summary of the following material:

${pageInfo}
Content:
${content.substring(0, 8000)}

Your summary should include:
1. **Main Topic/Theme**
2. **Key Concepts** (bulleted list)
3. **Important Details** (3-5 points)
4. **Takeaways** (what students should remember)

Format your response in markdown with clear headings and bullet points.`

    try {
      const response = await this.client.chat.completions.create({
        model: 'llama-3.3-70b-versatile',
        messages: [
          {
            role: 'system',
            content: 'You are an expert at creating clear, comprehensive summaries of educational material. Always format output in markdown.'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.7,
        max_tokens: 2000
      })

      return response.choices[0].message.content
    } catch (error) {
      console.error('Backup summary error:', error)
      throw error
    }
  }
}

export const backupAiService = new BackupAiService()
