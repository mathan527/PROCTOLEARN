<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
    <!-- Header with Navigation -->
    <header class="bg-white shadow-md sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-8 py-4 flex justify-between items-center">
        <div class="flex items-center gap-8">
          <router-link to="/" class="text-2xl font-bold text-indigo-600 hover:text-indigo-700">
            🎓 CauchyMentor
          </router-link>
          <nav class="hidden md:flex gap-6">
            <router-link 
              v-if="authStore.user?.role === 'student'"
              to="/student/dashboard" 
              class="text-gray-600 hover:text-indigo-600 font-medium transition"
            >
              Dashboard
            </router-link>
            <router-link 
              v-if="authStore.user?.role === 'teacher'"
              to="/teacher/dashboard" 
              class="text-gray-600 hover:text-indigo-600 font-medium transition"
            >
              Dashboard
            </router-link>
            <router-link 
              to="/course-generator" 
              class="text-indigo-600 font-semibold border-b-2 border-indigo-600"
            >
              AI Courses
            </router-link>
          </nav>
        </div>
        <div class="flex items-center gap-4">
          <span class="text-gray-700">{{ authStore.user?.full_name || authStore.user?.email }}</span>
          <router-link 
            to="/profile" 
            class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
          >
            Profile
          </router-link>
          <button 
            @click="logout" 
            class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition"
          >
            Logout
          </button>
        </div>
      </div>
    </header>

    <div class="p-6 max-w-7xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-4xl font-bold text-gray-900 mb-2">🎓 AI Course Generator</h1>
        <p class="text-gray-600">Generate personalized learning paths with AI-powered courses</p>
      </div>

      <!-- Course Generation Form -->
      <div v-if="!courseGenerated" class="bg-white rounded-2xl shadow-xl p-8 mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-6">Create Your Course</h2>
        
        <form @submit.prevent="generateCourse" class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              What do you want to learn?
            </label>
            <input
              v-model="courseRequest.topic"
              type="text"
              placeholder="e.g., Machine Learning, Web Development, Calculus..."
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              required
            />
          </div>

          <div class="grid md:grid-cols-3 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Duration (Days)
              </label>
              <input
                v-model.number="courseRequest.duration_days"
                type="number"
                min="1"
                max="90"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                required
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Difficulty Level
              </label>
              <select
                v-model="courseRequest.difficulty"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                <option value="beginner">Beginner</option>
                <option value="medium">Medium</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Learning Style
              </label>
              <select
                v-model="courseRequest.learning_style"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                <option value="comprehensive">Comprehensive</option>
                <option value="practical">Hands-on Practical</option>
                <option value="theoretical">Theoretical</option>
                <option value="fast-track">Fast Track</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            :disabled="generating"
            class="w-full bg-indigo-600 text-white py-4 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ generating ? 'Generating Course...' : '✨ Generate Course' }}
          </button>
        </form>
      </div>

      <!-- Loading State -->
      <div v-if="generating" class="bg-white rounded-2xl shadow-xl p-12 text-center">
        <div class="animate-spin rounded-full h-16 w-16 border-b-4 border-indigo-600 mx-auto mb-4"></div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">Creating Your Course...</h3>
        <p class="text-gray-600">This may take a moment. AI is designing your personalized learning path.</p>
      </div>

      <!-- Generated Course -->
      <div v-if="courseGenerated && courseData" class="space-y-6">
        <!-- Course Overview -->
        <div class="bg-white rounded-2xl shadow-xl p-8">
          <div class="flex justify-between items-start mb-6">
            <div>
              <h2 class="text-3xl font-bold text-gray-900 mb-2">{{ courseData.course_title }}</h2>
              <p class="text-gray-600 mb-4">{{ courseData.description }}</p>
              <div class="flex gap-3">
                <span class="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium">
                  {{ courseData.difficulty }}
                </span>
                <span class="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                  {{ courseData.total_days }} Days
                </span>
              </div>
            </div>
            <button
              @click="resetCourse"
              class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
            >
              New Course
            </button>
          </div>

          <div class="grid md:grid-cols-2 gap-6 mt-6">
            <div>
              <h3 class="font-semibold text-gray-900 mb-2">📚 Prerequisites</h3>
              <ul class="space-y-1">
                <li v-for="(prereq, idx) in courseData.prerequisites" :key="idx" class="text-gray-600 text-sm">
                  • {{ prereq }}
                </li>
              </ul>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 mb-2">🎯 Learning Outcomes</h3>
              <ul class="space-y-1">
                <li v-for="(outcome, idx) in courseData.learning_outcomes" :key="idx" class="text-gray-600 text-sm">
                  • {{ outcome }}
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Daily Lessons -->
        <div class="space-y-4">
          <div class="flex justify-between items-center">
            <h3 class="text-2xl font-bold text-gray-900">📖 Daily Lessons</h3>
            <div class="text-sm text-gray-600 bg-blue-50 px-4 py-2 rounded-lg border border-blue-200">
              💡 Click "📖 Read Lesson" to view full detailed content for each day
            </div>
          </div>
          
          <div
            v-for="lesson in courseData.daily_lessons"
            :key="lesson.day"
            class="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition"
          >
            <div class="flex justify-between items-start mb-4">
              <div>
                <div class="flex items-center gap-3 mb-2">
                  <span class="text-3xl font-bold text-indigo-600">Day {{ lesson.day }}</span>
                  <h4 class="text-xl font-semibold text-gray-900">{{ lesson.title }}</h4>
                </div>
                <p class="text-sm text-gray-500">⏱️ {{ lesson.estimated_time }}</p>
              </div>
              
              <div class="flex gap-2">
                <button
                  @click="viewDayContent(lesson)"
                  class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition text-sm font-medium shadow-sm"
                >
                  📖 Read Lesson
                </button>
                <button
                  v-if="isAssessmentDay(lesson.day)"
                  @click="takeAssessment(lesson.day)"
                  class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-sm font-medium shadow-sm"
                >
                  📝 Take Test
                </button>
              </div>
            </div>

            <div class="grid md:grid-cols-2 gap-4 mb-4">
              <div>
                <h5 class="font-semibold text-gray-700 mb-2 text-sm">🎯 Objectives:</h5>
                <ul class="space-y-1">
                  <li v-for="(obj, idx) in lesson.objectives" :key="idx" class="text-gray-600 text-sm">
                    • {{ obj }}
                  </li>
                </ul>
              </div>
              <div>
                <h5 class="font-semibold text-gray-700 mb-2 text-sm">📚 Topics:</h5>
                <ul class="space-y-1">
                  <li v-for="(topic, idx) in lesson.topics" :key="idx" class="text-gray-600 text-sm">
                    • {{ topic }}
                  </li>
                </ul>
              </div>
            </div>

            <p class="text-gray-600 text-sm mb-4">{{ lesson.content_summary }}</p>

            <div class="flex gap-4 text-sm">
              <div>
                <span class="font-semibold text-gray-700">Resources:</span>
                <span class="text-gray-600"> {{ lesson.resources.length }} items</span>
              </div>
              <div>
                <span class="font-semibold text-gray-700">Activities:</span>
                <span class="text-gray-600"> {{ lesson.practice_activities.length }} tasks</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Day Content Modal -->
      <div
        v-if="showDayContent"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto"
        @click.self="showDayContent = false"
      >
        <div class="bg-white rounded-2xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-y-auto p-8 my-8">
          <div class="flex justify-between items-start mb-6 sticky top-0 bg-white pb-4 border-b">
            <div>
              <h3 class="text-2xl font-bold text-gray-900 mb-2">
                Day {{ selectedLesson?.day }}: {{ selectedLesson?.title }}
              </h3>
              <p class="text-sm text-gray-500">⏱️ {{ selectedLesson?.estimated_time }}</p>
            </div>
            <button
              @click="showDayContent = false"
              class="text-gray-400 hover:text-gray-600 ml-4 flex-shrink-0"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div v-if="loadingDayContent" class="text-center py-12">
            <div class="animate-spin rounded-full h-12 w-12 border-b-4 border-indigo-600 mx-auto mb-4"></div>
            <p class="text-gray-600">Loading detailed lesson content...</p>
            <p class="text-sm text-gray-500 mt-2">AI is generating comprehensive learning materials for you</p>
          </div>

          <div v-else-if="dayContent" class="lesson-content">
            <div v-html="formatContent(dayContent)" class="text-gray-700 leading-relaxed"></div>
            
            <!-- Actions at bottom -->
            <div class="mt-8 pt-6 border-t flex justify-between items-center">
              <button
                @click="printContent"
                class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
              >
                🖨️ Print Lesson
              </button>
              <button
                @click="showDayContent = false"
                class="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition font-semibold"
              >
                ✓ Mark as Complete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'
import { useToast } from 'vue-toastification'
import { marked } from 'marked'

// Configure marked for better rendering
marked.setOptions({
  breaks: true,
  gfm: true,
  headerIds: true,
  mangle: false
})

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const logout = () => {
  authStore.logout()
  router.push('/')
}

const courseRequest = ref({
  topic: '',
  duration_days: 14,
  difficulty: 'medium',
  learning_style: 'comprehensive'
})

const generating = ref(false)
const courseGenerated = ref(false)
const courseData = ref(null)
const showDayContent = ref(false)
const selectedLesson = ref(null)
const dayContent = ref('')
const loadingDayContent = ref(false)

// Check if viewing an existing course
onMounted(() => {
  const viewCourseData = sessionStorage.getItem('viewCourse')
  if (viewCourseData) {
    try {
      const { course, metadata } = JSON.parse(viewCourseData)
      
      if (!course) {
        console.error('No course data found')
        sessionStorage.removeItem('viewCourse')
        return
      }
      
      // Parse the course content (it's stored as a string in the database)
      let courseContent = course.content
      
      if (typeof courseContent === 'string') {
        try {
          courseContent = JSON.parse(courseContent)
        } catch (parseError) {
          console.error('Failed to parse course content:', parseError)
          sessionStorage.removeItem('viewCourse')
          toast.error('Failed to parse course data')
          return
        }
      }
      
      if (!courseContent || !courseContent.daily_lessons) {
        console.error('Invalid course structure - missing daily_lessons:', courseContent)
        sessionStorage.removeItem('viewCourse')
        toast.error('Invalid course structure')
        return
      }
      
      // Set up the course data
      courseData.value = courseContent
      courseGenerated.value = true
      
      // Set the course request with the original parameters
      courseRequest.value = {
        topic: course.topic || 'Unknown Topic',
        duration_days: courseContent.total_days || metadata?.duration_days || 14,
        difficulty: courseContent.difficulty || metadata?.difficulty || 'medium',
        learning_style: metadata?.learning_style || 'comprehensive'
      }
      
      toast.success(`Loaded: ${course.topic}`)
      
      // Clear the session storage
      sessionStorage.removeItem('viewCourse')
      
      // Auto-load first day content
      if (courseData.value.daily_lessons.length > 0) {
        setTimeout(() => {
          viewDayContent(courseData.value.daily_lessons[0])
        }, 500)
      }
    } catch (error) {
      console.error('Failed to load course from session:', error)
      sessionStorage.removeItem('viewCourse')
      toast.error('Failed to load course')
    }
  }
})

const generateCourse = async () => {
  generating.value = true
  try {
    const response = await api.post('/ai/generate-course', courseRequest.value)
    courseData.value = response.data.course
    courseGenerated.value = true
    toast.success('Course generated successfully!')
    
    // Automatically load first day content as preview
    if (courseData.value.daily_lessons && courseData.value.daily_lessons.length > 0) {
      toast.info('Loading Day 1 preview...', { timeout: 2000 })
      setTimeout(() => {
        viewDayContent(courseData.value.daily_lessons[0])
      }, 1000)
    }
  } catch (error) {
    console.error('Failed to generate course:', error)
    toast.error(error.response?.data?.detail || 'Failed to generate course')
  } finally {
    generating.value = false
  }
}

const resetCourse = () => {
  courseGenerated.value = false
  courseData.value = null
  courseRequest.value = {
    topic: '',
    duration_days: 14,
    difficulty: 'medium',
    learning_style: 'comprehensive'
  }
}

const isAssessmentDay = (day) => {
  return courseData.value?.assessment_days?.includes(day) || false
}

const viewDayContent = async (lesson) => {
  selectedLesson.value = lesson
  showDayContent.value = true
  loadingDayContent.value = true
  dayContent.value = ''

  try {
    const response = await api.post('/ai/generate-day-content', {
      topic: courseRequest.value.topic,
      day_number: lesson.day,
      lesson_title: lesson.title,
      objectives: lesson.objectives
    })
    dayContent.value = response.data.content
  } catch (error) {
    console.error('Failed to load day content:', error)
    toast.error('Failed to load lesson content')
  } finally {
    loadingDayContent.value = false
  }
}

const takeAssessment = async (day) => {
  try {
    // Get topics covered up to this day
    const coveredTopics = courseData.value.daily_lessons
      .filter(lesson => lesson.day <= day)
      .flatMap(lesson => lesson.topics)

    const response = await api.post('/ai/create-course-test', {
      topic: courseRequest.value.topic,
      day_number: day,
      covered_topics: coveredTopics,
      num_questions: 5,
      difficulty: courseRequest.value.difficulty
    })

    const testId = response.data.test_id
    toast.success('Assessment created! Redirecting...')
    
    setTimeout(() => {
      router.push(`/test/${testId}`)
    }, 1000)
  } catch (error) {
    console.error('Failed to create assessment:', error)
    toast.error('Failed to create assessment')
  }
}

const formatContent = (content) => {
  if (!content) return ''
  
  try {
    // Use marked to parse markdown to HTML
    return marked.parse(content)
  } catch (error) {
    console.error('Failed to parse markdown:', error)
    // Fallback to plain text
    return content.replace(/\n/g, '<br>')
  }
}

const printContent = () => {
  window.print()
}

</script>

<style scoped>
.lesson-content {
  font-size: 1.05rem;
  line-height: 1.8;
  color: #1f2937;
}

/* Markdown Headers */
.lesson-content :deep(h1) {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-top: 2rem;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 3px solid #6366f1;
}

.lesson-content :deep(h2) {
  font-size: 1.75rem;
  font-weight: 700;
  color: #374151;
  margin-top: 2rem;
  margin-bottom: 1rem;
  padding-bottom: 0.3rem;
  border-bottom: 2px solid #e5e7eb;
}

.lesson-content :deep(h3) {
  font-size: 1.5rem;
  font-weight: 600;
  color: #4b5563;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}

.lesson-content :deep(h4) {
  font-size: 1.25rem;
  font-weight: 600;
  color: #6b7280;
  margin-top: 1.25rem;
  margin-bottom: 0.5rem;
}

/* Paragraphs and Text */
.lesson-content :deep(p) {
  margin-bottom: 1.25rem;
  color: #374151;
  line-height: 1.8;
}

.lesson-content :deep(strong) {
  font-weight: 700;
  color: #1f2937;
}

.lesson-content :deep(em) {
  font-style: italic;
  color: #4b5563;
}

/* Lists */
.lesson-content :deep(ul),
.lesson-content :deep(ol) {
  margin-left: 2rem;
  margin-bottom: 1.5rem;
  padding-left: 0.5rem;
}

.lesson-content :deep(ul) {
  list-style-type: disc;
}

.lesson-content :deep(ol) {
  list-style-type: decimal;
}

.lesson-content :deep(li) {
  margin-bottom: 0.75rem;
  padding-left: 0.5rem;
  color: #374151;
  line-height: 1.7;
}

.lesson-content :deep(li p) {
  margin-bottom: 0.5rem;
}

.lesson-content :deep(ul ul),
.lesson-content :deep(ol ul) {
  list-style-type: circle;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}

.lesson-content :deep(ol ol),
.lesson-content :deep(ul ol) {
  list-style-type: lower-alpha;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}

/* Code */
.lesson-content :deep(code) {
  background-color: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-family: 'Fira Code', 'Courier New', monospace;
  font-size: 0.9em;
  color: #dc2626;
  border: 1px solid #e5e7eb;
}

.lesson-content :deep(pre) {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border: 1px solid #334155;
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin: 1.5rem 0;
  overflow-x: auto;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.lesson-content :deep(pre code) {
  background: transparent;
  padding: 0;
  border: none;
  color: #e2e8f0;
  font-size: 0.95em;
  line-height: 1.6;
}

/* Blockquotes */
.lesson-content :deep(blockquote) {
  border-left: 4px solid #6366f1;
  padding: 1rem 1.5rem;
  margin: 1.5rem 0;
  background: linear-gradient(to right, #eef2ff, transparent);
  border-radius: 0 0.5rem 0.5rem 0;
  font-style: italic;
  color: #4b5563;
}

.lesson-content :deep(blockquote p) {
  margin-bottom: 0.5rem;
}

/* Tables */
.lesson-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5rem 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-radius: 0.5rem;
  overflow: hidden;
}

.lesson-content :deep(thead) {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: white;
}

.lesson-content :deep(th) {
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid #4f46e5;
}

.lesson-content :deep(td) {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.lesson-content :deep(tbody tr:hover) {
  background-color: #f9fafb;
}

.lesson-content :deep(tbody tr:last-child td) {
  border-bottom: none;
}

/* Horizontal Rule */
.lesson-content :deep(hr) {
  border: none;
  height: 2px;
  background: linear-gradient(to right, transparent, #e5e7eb, transparent);
  margin: 2rem 0;
}

/* Links */
.lesson-content :deep(a) {
  color: #6366f1;
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: all 0.2s;
}

.lesson-content :deep(a:hover) {
  color: #4f46e5;
  border-bottom-color: #4f46e5;
}

/* Images */
.lesson-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 0.5rem;
  margin: 1.5rem 0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

@media print {
  .lesson-content {
    font-size: 12pt;
  }
  
  .lesson-content :deep(pre) {
    background: #f3f4f6 !important;
    border: 1px solid #d1d5db !important;
  }
  
  .lesson-content :deep(pre code) {
    color: #1f2937 !important;
  }
  
  header, button {
    display: none !important;
  }
}
</style>
