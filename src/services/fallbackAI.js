// Fallback AI service for when backend is unavailable
// Uses simple pattern matching and cached responses

class FallbackAIService {
  constructor() {
    this.responses = {
      summarize: (content) => this.generateSummary(content),
      explain: (content) => this.generateExplanation(content),
      questions: (content) => this.generateQuestions(content),
      terms: (content) => this.extractTerms(content)
    }
  }

  async getStudyHelp(question, context = '') {
    const lowerQuestion = question.toLowerCase()
    
    // Pattern matching for different types of questions
    if (lowerQuestion.includes('summar')) {
      return this.generateSummary(context)
    } else if (lowerQuestion.includes('explain') || lowerQuestion.includes('what is')) {
      return this.generateExplanation(context, question)
    } else if (lowerQuestion.includes('question') || lowerQuestion.includes('practice')) {
      return this.generateQuestions(context)
    } else if (lowerQuestion.includes('term') || lowerQuestion.includes('definition')) {
      return this.extractTerms(context)
    } else if (lowerQuestion.includes('key point') || lowerQuestion.includes('main point')) {
      return this.extractKeyPoints(context)
    } else {
      return this.generateContextualAnswer(question, context)
    }
  }

  generateSummary(content) {
    if (!content || content.length < 50) {
      return '**Summary:**\n\nThe provided content is too short to summarize effectively. Please ensure you have selected material with sufficient content.'
    }

    const sentences = content.match(/[^.!?]+[.!?]+/g) || []
    const wordCount = content.split(/\s+/).length
    const avgSentenceLength = wordCount / sentences.length

    const summary = `**Summary:**\n\n` +
      `📊 **Content Overview:**\n` +
      `- Total words: ${wordCount}\n` +
      `- Sentences: ${sentences.length}\n` +
      `- Average sentence length: ${Math.round(avgSentenceLength)} words\n\n` +
      `**Key Content:**\n\n` +
      `${sentences.slice(0, 5).join(' ')}\n\n` +
      `*Note: This is a simplified summary. For better AI analysis, please ensure the backend service is running.*`

    return summary
  }

  generateExplanation(content, question) {
    const relevantText = this.findRelevantText(content, question)
    
    return `**Explanation:**\n\n` +
      `Based on the material provided:\n\n` +
      `${relevantText.substring(0, 500)}...\n\n` +
      `**Key Points:**\n` +
      `- The material discusses various concepts related to your question\n` +
      `- For detailed explanations, consider consulting additional resources\n` +
      `- Review the material thoroughly for comprehensive understanding\n\n` +
      `*Note: For more detailed AI-powered explanations, please ensure the backend service is connected.*`
  }

  generateQuestions(content) {
    const sentences = content.match(/[^.!?]+[.!?]+/g) || []
    const questions = []

    // Generate simple questions from content
    for (let i = 0; i < Math.min(5, sentences.length); i++) {
      const sentence = sentences[i * Math.floor(sentences.length / 5)]
      if (sentence && sentence.length > 20) {
        questions.push({
          question: `What can you tell me about: "${sentence.substring(0, 50)}..."?`,
          type: 'open-ended'
        })
      }
    }

    return `**Practice Questions:**\n\n` +
      questions.map((q, i) => `${i + 1}. ${q.question}`).join('\n\n') +
      `\n\n*Note: For AI-generated practice questions with answers, please ensure the backend service is running.*`
  }

  extractTerms(content) {
    // Simple term extraction (words with capital letters or repeated frequently)
    const words = content.match(/\b[A-Z][a-z]+\b/g) || []
    const wordFrequency = {}
    
    words.forEach(word => {
      if (word.length > 3) {
        wordFrequency[word] = (wordFrequency[word] || 0) + 1
      }
    })

    const terms = Object.entries(wordFrequency)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([term]) => term)

    return `**Important Terms:**\n\n` +
      terms.map((term, i) => `${i + 1}. **${term}**`).join('\n') +
      `\n\n*Note: For detailed definitions and explanations, please ensure the backend service is running.*`
  }

  extractKeyPoints(content) {
    const sentences = content.match(/[^.!?]+[.!?]+/g) || []
    const keyPoints = sentences.slice(0, 5)

    return `**Key Points:**\n\n` +
      keyPoints.map((point, i) => `${i + 1}. ${point.trim()}`).join('\n\n') +
      `\n\n*Note: For AI-powered key point extraction, please ensure the backend service is running.*`
  }

  findRelevantText(content, question) {
    // Simple relevance: find text near question keywords
    const keywords = question.toLowerCase().split(' ').filter(w => w.length > 3)
    const contentLower = content.toLowerCase()
    
    for (const keyword of keywords) {
      const index = contentLower.indexOf(keyword)
      if (index !== -1) {
        const start = Math.max(0, index - 200)
        const end = Math.min(content.length, index + 300)
        return content.substring(start, end)
      }
    }
    
    return content.substring(0, 500)
  }

  generateContextualAnswer(question, context) {
    const relevantText = this.findRelevantText(context, question)
    
    return `**Answer:**\n\n` +
      `Based on the question "${question}", here's what I found in the material:\n\n` +
      `${relevantText}\n\n` +
      `**Additional Information:**\n` +
      `- Review the full material for complete context\n` +
      `- Consider cross-referencing with other resources\n` +
      `- For deeper AI analysis and answers, please ensure the backend service is connected\n\n` +
      `*This is a basic text-matching response. For AI-powered answers, please check your backend connection.*`
  }
}

export const fallbackAI = new FallbackAIService()
