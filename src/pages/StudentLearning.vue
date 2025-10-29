<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="max-w-7xl mx-auto space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">AI Learning Assistant</h1>
          <p class="text-sm text-gray-600 mt-1">Upload your study materials and learn with AI</p>
        </div>
        <Button @click="showUploadModal = true">
          Upload Material
        </Button>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card variant="default" class-name="border-l-4 border-l-black">
          <div class="space-y-2">
            <p class="text-sm text-gray-600">My Materials</p>
            <p class="text-3xl font-bold text-gray-900">{{ myMaterials.length }}</p>
          </div>
        </Card>

        <Card variant="default" class-name="border-l-4 border-l-gray-400">
          <div class="space-y-2">
            <p class="text-sm text-gray-600">Questions Asked</p>
            <p class="text-3xl font-bold text-gray-900">{{ totalQuestionsAsked }}</p>
          </div>
        </Card>

        <Card variant="default" class-name="border-l-4 border-l-gray-400">
          <div class="space-y-2">
            <p class="text-sm text-gray-600">Study Sessions</p>
            <p class="text-3xl font-bold text-gray-900">{{ studySessions.length }}</p>
          </div>
        </Card>

        <Card variant="default" class-name="border-l-4 border-l-gray-400">
          <div class="space-y-2">
            <p class="text-sm text-gray-600">Hours Studied</p>
            <p class="text-3xl font-bold text-gray-900">{{ totalHoursStudied }}</p>
          </div>
        </Card>
      </div>

      <!-- Main Content -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Materials List -->
        <div class="lg:col-span-2 space-y-4">
          <Card variant="elevated">
            <template #header>
              <div class="flex items-center justify-between">
                <h2 class="text-lg font-semibold text-gray-900">My Study Materials</h2>
                <div class="flex items-center space-x-2">
                  <input
                    v-model="searchQuery"
                    type="text"
                    placeholder="Search materials..."
                    class="text-sm border border-gray-300 rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-black"
                  />
                </div>
              </div>
            </template>

            <div v-if="loading" class="text-center py-12">
              <div class="inline-block w-8 h-8 border-4 border-gray-200 border-t-black rounded-full animate-spin"></div>
              <p class="text-sm text-gray-600 mt-4">Loading materials...</p>
            </div>

            <div v-else-if="filteredMaterials.length === 0" class="text-center py-12">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              <p class="text-sm text-gray-600 mt-4">No materials yet</p>
              <Button
                variant="outline"
                class-name="mt-4"
                @click="showUploadModal = true"
              >
                Upload Your First Material
              </Button>
            </div>

            <div v-else class="space-y-3">
              <div
                v-for="material in filteredMaterials"
                :key="material.id"
                @click="selectMaterial(material)"
                class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all cursor-pointer"
                :class="selectedMaterial?.id === material.id ? 'border-black bg-gray-50' : ''"
              >
                <div class="flex items-start justify-between mb-2">
                  <div class="flex-1">
                    <h3 class="text-base font-semibold text-gray-900">{{ material.name }}</h3>
                    <p v-if="material.content" class="text-sm text-gray-600 mt-1">{{ material.content.substring(0, 150) }}...</p>
                    <p v-else class="text-sm text-gray-600 mt-1">{{ material.content_length }} characters</p>
                  </div>
                  <Badge variant="secondary">{{ material.type }}</Badge>
                </div>
                <div class="flex items-center justify-between text-xs text-gray-500">
                  <span>{{ formatDate(material.created_at) }}</span>
                  <span>{{ material.content_length || (material.content?.length || 0) }} characters</span>
                </div>
              </div>
            </div>
          </Card>
        </div>

        <!-- Study Assistant -->
        <div class="space-y-4">
          <Card variant="elevated">
            <template #header>
              <h2 class="text-lg font-semibold text-gray-900">Quick Study</h2>
            </template>

            <div v-if="!selectedMaterial" class="text-center py-8">
              <svg class="mx-auto h-10 w-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
              </svg>
              <p class="text-sm text-gray-600 mt-2">Select a material to start</p>
            </div>

            <div v-else class="space-y-4">
              <div class="bg-gray-50 border border-gray-200 rounded-md p-3">
                <p class="text-sm font-medium text-gray-900">{{ selectedMaterial.name }}</p>
                <p class="text-xs text-gray-600 mt-1">{{ selectedMaterial.content_length || selectedMaterial.content?.length || 0 }} characters</p>
              </div>

              <div class="space-y-3">
                <Button
                  @click="startStudySession"
                  class="w-full"
                  variant="default"
                >
                  Start Study Session
                </Button>
                <Button
                  @click="openAskQuestion"
                  class="w-full"
                  variant="outline"
                >
                  Ask Question
                </Button>
                <Button
                  @click="generatePracticeQuiz"
                  class="w-full"
                  variant="outline"
                >
                  Practice Quiz
                </Button>
                <Button
                  @click="getSummary"
                  class="w-full"
                  variant="outline"
                >
                  Get Summary
                </Button>
              </div>
            </div>
          </Card>

          <Card variant="default">
            <template #header>
              <h3 class="text-sm font-semibold text-gray-900">Recent Activity</h3>
            </template>
            <div class="space-y-2 text-sm">
              <div v-for="(activity, index) in recentActivity" :key="index" class="flex items-center space-x-2 text-gray-600">
                <span class="w-2 h-2 bg-black rounded-full"></span>
                <span>{{ activity }}</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>

    <!-- Upload Modal -->
    <div v-if="showUploadModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-xl font-semibold text-gray-900">Upload Study Material</h2>
            <button @click="showUploadModal = false" class="text-gray-400 hover:text-gray-600">
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-900 mb-2">Material Name</label>
              <Input
                v-model="uploadForm.name"
                placeholder="Enter material name"
                :disabled="uploading"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-900 mb-2">Type</label>
              <select
                v-model="uploadForm.type"
                :disabled="uploading"
                class="w-full h-10 rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black"
              >
                <option value="notes">Class Notes</option>
                <option value="textbook">Textbook Chapter</option>
                <option value="slides">Presentation Slides</option>
                <option value="reference">Reference Material</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-900 mb-2">Upload File</label>
              <div
                @click="triggerFileInput"
                @dragover.prevent="dragOver = true"
                @dragleave.prevent="dragOver = false"
                @drop.prevent="handleFileDrop"
                :class="[
                  'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
                  dragOver ? 'border-black bg-gray-50' : 'border-gray-300 hover:border-gray-400'
                ]"
              >
                <input
                  ref="fileInput"
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg"
                  @change="handleFileSelect"
                  class="hidden"
                />
                <div v-if="!uploadForm.file" class="space-y-2">
                  <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <div class="text-sm text-gray-600">
                    <span class="font-semibold text-black">Click to upload</span> or drag and drop
                  </div>
                  <div class="text-xs text-gray-500">PDF, PNG, JPG (max 10MB)</div>
                </div>
                <div v-else class="flex items-center justify-center space-x-3">
                  <svg class="h-8 w-8 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <div class="text-left">
                    <p class="text-sm font-medium text-gray-900">{{ uploadForm.file.name }}</p>
                    <p class="text-xs text-gray-500">{{ formatFileSize(uploadForm.file.size) }}</p>
                  </div>
                  <button
                    @click.stop="uploadForm.file = null"
                    class="text-gray-400 hover:text-gray-600"
                  >
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <div v-if="uploading" class="space-y-2">
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">Processing...</span>
                <span class="font-medium text-gray-900">{{ uploadProgress }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-black h-2 rounded-full transition-all duration-300"
                  :style="{ width: `${uploadProgress}%` }"
                ></div>
              </div>
            </div>

            <div class="flex justify-end space-x-3 pt-4">
              <Button
                variant="outline"
                @click="showUploadModal = false"
                :disabled="uploading"
              >
                Cancel
              </Button>
              <Button
                @click="uploadMaterial"
                :disabled="!canUpload || uploading"
              >
                {{ uploading ? 'Processing...' : 'Upload & Process' }}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Study Session Modal - Chatbot Style -->
    <div v-if="showStudySession" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-6xl w-full h-[85vh] flex flex-col shadow-2xl">
        <!-- Header -->
        <div class="flex items-center justify-between p-4 border-b bg-gradient-to-r from-blue-600 to-purple-600">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 rounded-full bg-white flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div>
              <h2 class="text-lg font-semibold text-white">AI Study Assistant</h2>
              <p class="text-xs text-blue-100">{{ selectedMaterial?.name }}</p>
            </div>
          </div>
          <button @click="endStudySession" class="text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2 transition">
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Chat Container -->
        <div class="flex-1 overflow-hidden flex">
          <!-- Material Preview Sidebar -->
          <div class="w-1/3 border-r bg-gray-50 overflow-y-auto p-4">
            <div class="sticky top-0 bg-gray-50 pb-2 mb-2">
              <h3 class="text-sm font-semibold text-gray-900 mb-1">Material Content</h3>
              <p class="text-xs text-gray-500">{{ selectedMaterial?.content_length || 0 }} characters</p>
            </div>
            <div class="prose prose-sm max-w-none">
              <div class="text-xs text-gray-700 whitespace-pre-wrap leading-relaxed">
                {{ selectedMaterial?.content?.substring(0, 3000) }}
                <span v-if="selectedMaterial?.content?.length > 3000" class="text-gray-400">...</span>
              </div>
            </div>
          </div>

          <!-- Chat Area -->
          <div class="flex-1 flex flex-col">
            <!-- Messages -->
            <div ref="chatMessages" class="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
              <!-- Welcome Message -->
              <div v-if="chatHistory.length === 0" class="flex justify-center items-center h-full">
                <div class="text-center max-w-md">
                  <div class="w-20 h-20 mx-auto mb-4 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                    <svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                  </div>
                  <h3 class="text-xl font-semibold text-gray-900 mb-2">Hello! I'm your AI Study Assistant</h3>
                  <p class="text-gray-600 mb-4">Ask me anything about the material you're studying. I'm here to help you understand better!</p>
                  <div class="flex flex-wrap gap-2 justify-center">
                    <button
                      v-for="prompt in quickPrompts"
                      :key="prompt"
                      @click="studyQuestion = prompt"
                      class="px-3 py-1.5 bg-white border border-gray-300 rounded-full text-xs text-gray-700 hover:bg-gray-100 transition"
                    >
                      {{ prompt }}
                    </button>
                  </div>
                </div>
              </div>

              <!-- Chat Messages -->
              <div v-for="(message, index) in chatHistory" :key="index" class="flex" :class="message.role === 'user' ? 'justify-end' : 'justify-start'">
                <div class="flex max-w-[80%]" :class="message.role === 'user' ? 'flex-row-reverse' : 'flex-row'">
                  <!-- Avatar -->
                  <div class="flex-shrink-0" :class="message.role === 'user' ? 'ml-3' : 'mr-3'">
                    <div v-if="message.role === 'user'" class="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white text-sm font-semibold">
                      {{ authStore.user?.full_name?.[0] || 'U' }}
                    </div>
                    <div v-else class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                      <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                    </div>
                  </div>

                  <!-- Message Bubble -->
                  <div>
                    <div
                      class="rounded-2xl px-4 py-3 shadow-sm"
                      :class="message.role === 'user'
                        ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                        : 'bg-white text-gray-800 border border-gray-200'"
                    >
                      <div v-if="message.role === 'user'" class="text-sm">{{ message.content }}</div>
                      <div v-else class="prose prose-sm max-w-none" v-html="message.content"></div>
                    </div>
                    <div class="text-xs text-gray-400 mt-1" :class="message.role === 'user' ? 'text-right mr-1' : 'ml-1'">
                      {{ message.timestamp }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- Typing Indicator -->
              <div v-if="askingQuestion" class="flex justify-start">
                <div class="flex">
                  <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center mr-3">
                    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <div class="bg-white rounded-2xl px-4 py-3 border border-gray-200">
                    <div class="flex space-x-2">
                      <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                      <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                      <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Input Area -->
            <div class="border-t bg-white p-4">
              <div class="flex items-end space-x-2">
                <div class="flex-1">
                  <textarea
                    v-model="studyQuestion"
                    @keydown.enter.exact.prevent="askStudyQuestion"
                    placeholder="Type your question here... (Press Enter to send)"
                    rows="1"
                    class="w-full rounded-xl border-2 border-gray-300 bg-gray-50 px-4 py-3 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition"
                    style="min-height: 48px; max-height: 120px"
                  ></textarea>
                </div>
                <button
                  @click="askStudyQuestion"
                  :disabled="!studyQuestion.trim() || askingQuestion"
                  class="flex-shrink-0 h-12 w-12 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white flex items-center justify-center hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </button>
              </div>
              <div class="flex items-center justify-between mt-2">
                <p class="text-xs text-gray-500">{{ chatHistory.length }} messages • {{ totalQuestionsAsked }} questions asked</p>
                <button
                  @click="clearChat"
                  class="text-xs text-gray-500 hover:text-gray-700 flex items-center space-x-1"
                >
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  <span>Clear chat</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Summary Modal -->
    <div v-if="showSummaryModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[85vh] flex flex-col shadow-2xl">
        <!-- Header -->
        <div class="flex items-center justify-between p-4 border-b bg-gradient-to-r from-green-600 to-teal-600">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 rounded-full bg-white flex items-center justify-center">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h2 class="text-lg font-semibold text-white">Material Summary</h2>
              <p class="text-xs text-green-100">{{ selectedMaterial?.name }}</p>
            </div>
          </div>
          <button @click="showSummaryModal = false" class="text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2 transition">
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Summary Content -->
        <div class="flex-1 overflow-y-auto p-6">
          <div v-if="loadingSummary" class="flex flex-col items-center justify-center h-full">
            <div class="w-12 h-12 border-4 border-green-200 border-t-green-600 rounded-full animate-spin"></div>
            <p class="text-sm text-gray-600 mt-4">Generating comprehensive summary...</p>
          </div>
          <div v-else class="prose prose-lg max-w-none" v-html="summaryContent"></div>
        </div>

        <!-- Footer -->
        <div class="p-4 border-t bg-gray-50 flex justify-between items-center">
          <p class="text-xs text-gray-500">AI-generated summary</p>
          <div class="flex space-x-2">
            <Button @click="getSummary" variant="outline" :disabled="loadingSummary">
              Regenerate
            </Button>
            <Button @click="showSummaryModal = false" variant="default">
              Close
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Practice Quiz Modal -->
    <div v-if="showQuizModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-3xl w-full max-h-[85vh] flex flex-col shadow-2xl">
        <!-- Header -->
        <div class="flex items-center justify-between p-4 border-b bg-gradient-to-r from-orange-600 to-red-600">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 rounded-full bg-white flex items-center justify-center">
              <svg class="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <div>
              <h2 class="text-lg font-semibold text-white">Practice Quiz</h2>
              <p class="text-xs text-orange-100">{{ selectedMaterial?.name }}</p>
            </div>
          </div>
          <button @click="closeQuizModal" class="text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2 transition">
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Quiz Content -->
        <div class="flex-1 overflow-y-auto p-6">
          <!-- Loading State -->
          <div v-if="loadingQuiz" class="flex flex-col items-center justify-center h-full">
            <div class="w-12 h-12 border-4 border-orange-200 border-t-orange-600 rounded-full animate-spin"></div>
            <p class="text-sm text-gray-600 mt-4">Generating quiz questions...</p>
          </div>

          <!-- Quiz Results -->
          <div v-else-if="showQuizResults" class="text-center">
            <div class="mb-6">
              <div class="w-24 h-24 mx-auto rounded-full flex items-center justify-center"
                   :class="quizScore >= 70 ? 'bg-green-100' : 'bg-yellow-100'">
                <span class="text-4xl font-bold" :class="quizScore >= 70 ? 'text-green-600' : 'text-yellow-600'">
                  {{ quizScore }}%
                </span>
              </div>
              <h3 class="text-2xl font-bold text-gray-900 mt-4">
                {{ quizScore >= 90 ? 'Excellent!' : quizScore >= 70 ? 'Good Job!' : 'Keep Practicing!' }}
              </h3>
              <p class="text-gray-600 mt-2">You scored {{ quizScore }}% on this quiz</p>
            </div>

            <!-- Answer Review -->
            <div class="space-y-4 text-left max-h-96 overflow-y-auto">
              <div v-for="(question, index) in quizQuestions" :key="index" class="border rounded-lg p-4"
                   :class="quizAnswers[index] === question.correct_answer ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'">
                <div class="flex items-start justify-between mb-2">
                  <p class="text-sm font-semibold text-gray-900">Q{{ index + 1 }}: {{ question.question }}</p>
                  <span class="text-xs px-2 py-1 rounded-full"
                        :class="quizAnswers[index] === question.correct_answer ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'">
                    {{ quizAnswers[index] === question.correct_answer ? '✓ Correct' : '✗ Incorrect' }}
                  </span>
                </div>
                <div class="mt-2 space-y-1 text-sm">
                  <p class="text-gray-700">Your answer: <span class="font-medium">{{ quizAnswers[index] || 'Not answered' }}</span></p>
                  <p class="text-green-700">Correct answer: <span class="font-medium">{{ question.correct_answer }}</span></p>
                  <p class="text-gray-600 text-xs mt-2">{{ question.explanation }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Quiz Questions -->
          <div v-else-if="quizQuestions.length > 0">
            <div class="mb-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-700">
                  Question {{ currentQuestionIndex + 1 }} of {{ quizQuestions.length }}
                </span>
                <Badge :variant="quizAnswers[currentQuestionIndex] ? 'default' : 'secondary'">
                  {{ quizAnswers[currentQuestionIndex] ? 'Answered' : 'Not answered' }}
                </Badge>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-orange-600 h-2 rounded-full transition-all"
                     :style="{ width: `${((currentQuestionIndex + 1) / quizQuestions.length) * 100}%` }">
                </div>
              </div>
            </div>

            <div class="bg-gray-50 rounded-lg p-6 mb-6">
              <p class="text-lg font-semibold text-gray-900 mb-4">{{ quizQuestions[currentQuestionIndex].question }}</p>
              
              <div class="space-y-3">
                <div v-for="(option, optIndex) in quizQuestions[currentQuestionIndex].options" :key="optIndex"
                     @click="selectQuizAnswer(option)"
                     class="p-4 border-2 rounded-lg cursor-pointer transition-all"
                     :class="quizAnswers[currentQuestionIndex] === option 
                       ? 'border-orange-600 bg-orange-50' 
                       : 'border-gray-300 hover:border-gray-400 bg-white'">
                  <div class="flex items-center">
                    <div class="w-5 h-5 rounded-full border-2 mr-3 flex items-center justify-center"
                         :class="quizAnswers[currentQuestionIndex] === option 
                           ? 'border-orange-600 bg-orange-600' 
                           : 'border-gray-400'">
                      <div v-if="quizAnswers[currentQuestionIndex] === option" class="w-2 h-2 rounded-full bg-white"></div>
                    </div>
                    <span class="text-gray-900">{{ option }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="p-4 border-t bg-gray-50">
          <div v-if="!showQuizResults && !loadingQuiz" class="flex justify-between">
            <Button @click="previousQuestion" variant="outline" :disabled="currentQuestionIndex === 0">
              Previous
            </Button>
            <div class="flex space-x-2">
              <Button v-if="currentQuestionIndex < quizQuestions.length - 1" @click="nextQuestion" variant="default">
                Next
              </Button>
              <Button v-else @click="submitQuiz" variant="default">
                Submit Quiz
              </Button>
            </div>
          </div>
          <div v-else-if="showQuizResults" class="flex justify-between">
            <Button @click="restartQuiz" variant="outline">
              Retry Quiz
            </Button>
            <Button @click="closeQuizModal" variant="default">
              Close
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { marked } from 'marked'
import { aiService } from '@/services/aiService'
import { useAuthStore } from '@/stores/auth'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Badge from '@/components/ui/Badge.vue'
import { useToast } from 'vue-toastification'

const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()

const myMaterials = ref([])
const selectedMaterial = ref(null)
const loading = ref(false)
const searchQuery = ref('')
const showUploadModal = ref(false)
const showStudySession = ref(false)
const showSummaryModal = ref(false)
const showQuizModal = ref(false)
const studySessions = ref([])
const totalQuestionsAsked = ref(0)
const recentActivity = ref([])

const uploadForm = ref({
  name: '',
  type: 'notes',
  file: null
})

const uploading = ref(false)
const uploadProgress = ref(0)
const dragOver = ref(false)
const fileInput = ref(null)

const studyQuestion = ref('')
const studyAnswer = ref('')
const askingQuestion = ref(false)
const chatHistory = ref([])
const chatMessages = ref(null)
const quickPrompts = ref([
  'Summarize the main points',
  'Explain the key concepts',
  'Give me practice questions',
  'What are the important terms?'
])

// Summary state
const summaryContent = ref('')
const loadingSummary = ref(false)

// Quiz state
const quizQuestions = ref([])
const currentQuestionIndex = ref(0)
const quizAnswers = ref([])
const showQuizResults = ref(false)
const loadingQuiz = ref(false)

const totalHoursStudied = computed(() => {
  return Math.round(studySessions.value.reduce((sum, s) => sum + (s.duration || 0), 0) / 60)
})

const filteredMaterials = computed(() => {
  if (!searchQuery.value) return myMaterials.value
  const query = searchQuery.value.toLowerCase()
  return myMaterials.value.filter(m =>
    (m.name || '').toLowerCase().includes(query) ||
    (m.content || '').toLowerCase().includes(query)
  )
})

const canUpload = computed(() => {
  return uploadForm.value.name.trim() && uploadForm.value.file
})

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) validateAndSetFile(file)
}

const handleFileDrop = (event) => {
  dragOver.value = false
  const file = event.dataTransfer.files[0]
  if (file) validateAndSetFile(file)
}

const validateAndSetFile = (file) => {
  const validTypes = ['application/pdf', 'image/png', 'image/jpeg']
  const maxSize = 10 * 1024 * 1024

  if (!validTypes.includes(file.type)) {
    toast.error('Invalid file type. Please upload PDF, PNG, or JPEG files.')
    return
  }

  if (file.size > maxSize) {
    toast.error('File size exceeds 10MB limit.')
    return
  }

  uploadForm.value.file = file
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const uploadMaterial = async () => {
  if (!canUpload.value) return
  
  if (!authStore.user?.id) {
    toast.error('Please log in to upload materials')
    return
  }

  try {
    uploading.value = true
    uploadProgress.value = 30

    const result = await aiService.uploadMaterial(
      uploadForm.value.file,
      uploadForm.value.name,
      uploadForm.value.type,
      authStore.user.id
    )

    uploadProgress.value = 100

    myMaterials.value.unshift({
      id: result.material_id,
      name: uploadForm.value.name,
      type: uploadForm.value.type,
      content: result.extracted_text,
      created_at: new Date().toISOString()
    })

    toast.success(`Successfully extracted ${result.text_length} characters`)
    
    uploadForm.value = { name: '', type: 'notes', file: null }
    showUploadModal.value = false
    uploadProgress.value = 0
    
    recentActivity.value.unshift(`Uploaded "${uploadForm.value.name}"`)
  } catch (error) {
    console.error('Upload failed:', error)
    console.error('Error details:', error.response?.data)
    console.error('Error message:', JSON.stringify(error.response?.data, null, 2))
    console.error('Status:', error.response?.status)
    if (error.response?.status === 503) {
      toast.error('AI service is unavailable. Please make sure both backend and AI service are running.')
    } else {
      toast.error(error.response?.data?.detail || 'Failed to upload material')
    }
  } finally {
    uploading.value = false
  }
}

const selectMaterial = async (material) => {
  try {
    // If material already has content, use it
    if (material.content) {
      selectedMaterial.value = material
      return
    }
    
    // Otherwise, fetch the full material with content
    loading.value = true
    const fullMaterial = await aiService.getMaterial(material.id)
    selectedMaterial.value = fullMaterial
  } catch (error) {
    console.error('Failed to load material:', error)
    toast.error('Failed to load material details')
  } finally {
    loading.value = false
  }
}

const startStudySession = () => {
  showStudySession.value = true
  const sessionStart = Date.now()
  studySessions.value.push({
    material: selectedMaterial.value.name,
    start: sessionStart,
    duration: 0
  })
  recentActivity.value.unshift(`Started studying "${selectedMaterial.value.name}"`)
}

const endStudySession = () => {
  if (studySessions.value.length > 0) {
    const lastSession = studySessions.value[studySessions.value.length - 1]
    lastSession.duration = Math.round((Date.now() - lastSession.start) / 1000 / 60)
  }
  showStudySession.value = false
  chatHistory.value = []
  studyQuestion.value = ''
  studyAnswer.value = ''
}

const askStudyQuestion = async () => {
  if (!studyQuestion.value.trim()) return
  
  if (!selectedMaterial.value?.content) {
    toast.error('Material content not loaded. Please select the material again.')
    return
  }

  const userQuestion = studyQuestion.value
  const timestamp = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
  
  // Add user message to chat
  chatHistory.value.push({
    role: 'user',
    content: userQuestion,
    timestamp
  })

  studyQuestion.value = '' // Clear input immediately

  try {
    askingQuestion.value = true
    totalQuestionsAsked.value++

    const answer = await aiService.getStudyHelp(
      userQuestion,
      selectedMaterial.value.content.substring(0, 2000),
      authStore.user?.id
    )

    // Add AI response to chat
    chatHistory.value.push({
      role: 'assistant',
      content: marked(answer),
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    })

    // Scroll to bottom
    setTimeout(() => {
      if (chatMessages.value) {
        chatMessages.value.scrollTop = chatMessages.value.scrollHeight
      }
    }, 100)

    recentActivity.value.unshift(`Asked question about "${selectedMaterial.value.name}"`)
  } catch (error) {
    console.error('Failed to get answer:', error)
    console.error('Error response:', error.response)
    console.error('Error data:', error.response?.data)
    console.error('Error status:', error.response?.status)
    console.error('Error config:', error.config)
    
    // Check if it's a backend error but we got a response from backup
    if (error.message && !error.message.includes('AI service unavailable')) {
      // This means backup AI worked but backend failed
      toast.warning('⚠️ Using offline mode - your question history won\'t be saved', {
        duration: 5000
      })
      // Don't remove the message - backup worked!
    } else {
      // Complete failure
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to get answer from AI'
      toast.error(errorMessage)
      
      // Remove user message if completely failed
      chatHistory.value.pop()
    }
  } finally {
    askingQuestion.value = false
  }
}

const clearChat = () => {
  if (confirm('Clear all messages in this chat?')) {
    chatHistory.value = []
    totalQuestionsAsked.value = 0
  }
}

const openAskQuestion = () => {
  // Open the study session modal which has the Ask AI feature
  if (selectedMaterial.value) {
    startStudySession()
  } else {
    toast.error('Please select a material first')
  }
}

const generatePracticeQuiz = async () => {
  if (!selectedMaterial.value) {
    toast.error('Please select a material first')
    return
  }
  
  try {
    loadingQuiz.value = true
    showQuizModal.value = true
    quizQuestions.value = []
    currentQuestionIndex.value = 0
    quizAnswers.value = []
    showQuizResults.value = false
    
    toast.info('Generating practice quiz... This may take a moment')
    const response = await aiService.generateQuestions(selectedMaterial.value.id, {
      numQuestions: 5,
      difficulty: 'medium',
      questionTypes: ['multiple_choice', 'true_false']
    })
    
    quizQuestions.value = response.questions || []
    quizAnswers.value = new Array(quizQuestions.value.length).fill(null)
    toast.success(`Generated ${quizQuestions.value.length} practice questions!`)
  } catch (error) {
    console.error('Failed to generate quiz:', error)
    toast.error('Failed to generate practice quiz')
    showQuizModal.value = false
  } finally {
    loadingQuiz.value = false
  }
}

const getSummary = async () => {
  if (!selectedMaterial.value?.id) {
    toast.error('Material not loaded. Please select the material again.')
    return
  }
  
  try {
    loadingSummary.value = true
    showSummaryModal.value = true
    summaryContent.value = ''
    
    toast.info('Generating summary... This may take a moment')
    const summary = await aiService.getSummary(selectedMaterial.value.id)
    summaryContent.value = marked(summary)
    toast.success('Summary generated!')
  } catch (error) {
    console.error('Failed to generate summary:', error)
    toast.error(error.response?.data?.detail || 'Failed to generate summary')
    showSummaryModal.value = false
  } finally {
    loadingSummary.value = false
  }
}

// Quiz functions
const selectQuizAnswer = (answer) => {
  quizAnswers.value[currentQuestionIndex.value] = answer
}

const nextQuestion = () => {
  if (currentQuestionIndex.value < quizQuestions.value.length - 1) {
    currentQuestionIndex.value++
  }
}

const previousQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
  }
}

const submitQuiz = () => {
  showQuizResults.value = true
}

const restartQuiz = () => {
  currentQuestionIndex.value = 0
  quizAnswers.value = new Array(quizQuestions.value.length).fill(null)
  showQuizResults.value = false
}

const closeQuizModal = () => {
  showQuizModal.value = false
  quizQuestions.value = []
  currentQuestionIndex.value = 0
  quizAnswers.value = []
  showQuizResults.value = false
}

const quizScore = computed(() => {
  if (!showQuizResults.value || quizQuestions.value.length === 0) return 0
  let correct = 0
  quizQuestions.value.forEach((q, i) => {
    if (quizAnswers.value[i] === q.correct_answer) {
      correct++
    }
  })
  return Math.round((correct / quizQuestions.value.length) * 100)
})

const loadMaterials = async () => {
  if (!authStore.user?.id) {
    console.warn('User not logged in')
    router.push('/login')
    return
  }
  
  try {
    loading.value = true
    const response = await aiService.getMaterials(authStore.user.id)
    myMaterials.value = response || []
  } catch (error) {
    console.error('Failed to load materials:', error)
    console.error('Error details:', error.response?.data)
    console.error('Error message:', JSON.stringify(error.response?.data, null, 2))
    console.error('Status:', error.response?.status)
    if (error.response?.status === 401) {
      toast.error('Please log in again')
    } else if (error.response?.status === 503) {
      toast.error('AI service is unavailable. Please make sure it is running.')
    } else {
      toast.error(error.response?.data?.detail || 'Failed to load materials')
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadMaterials()
  recentActivity.value = [
    'Welcome to AI Learning Assistant',
    'Upload materials to get started'
  ]
})
</script>
