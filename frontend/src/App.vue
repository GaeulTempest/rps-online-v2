<template>
  <div id="app" class="min-h-screen bg-gradient-to-br from-blue-900 to-purple-900">
    <header class="bg-black bg-opacity-20 backdrop-blur-sm">
      <div class="container mx-auto px-4 py-6">
        <h1 class="text-3xl font-bold text-white text-center">
          🪨📄✂️ Rock Paper Scissors Online
        </h1>
      </div>
    </header>

    <main class="container mx-auto px-4 py-8">
      <Lobby v-if="currentView === 'lobby'" @join-game="handleJoinGame" />
      <GameRoom 
        v-else-if="currentView === 'game'" 
        :room-id="roomId" 
        :player-id="playerId"
        @leave-game="handleLeaveGame"
      />
    </main>

    <!-- Loading Overlay -->
    <div v-if="isLoading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-8 text-center">
        <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-lg font-semibold">{{ loadingMessage }}</p>
      </div>
    </div>

    <!-- Error Modal -->
    <div v-if="error" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-8 max-w-md mx-4">
        <h3 class="text-xl font-bold text-red-600 mb-4">Error</h3>
        <p class="text-gray-700 mb-6">{{ error }}</p>
        <button 
          @click="clearError" 
          class="w-full bg-red-600 text-white py-2 px-4 rounded hover:bg-red-700 transition-colors"
        >
          OK
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Lobby from './components/Lobby.vue'
import GameRoom from './components/GameRoom.vue'
import { generatePlayerId } from './utils/camera.js'

const currentView = ref('lobby')
const roomId = ref('')
const playerId = ref('')
const isLoading = ref(false)
const loadingMessage = ref('')
const error = ref('')

onMounted(() => {
  // Generate unique player ID
  playerId.value = generatePlayerId()
})

const handleJoinGame = (data) => {
  roomId.value = data.roomId
  currentView.value = 'game'
}

const handleLeaveGame = () => {
  currentView.value = 'lobby'
  roomId.value = ''
}

const showLoading = (message) => {
  isLoading.value = true
  loadingMessage.value = message
}

const hideLoading = () => {
  isLoading.value = false
  loadingMessage.value = ''
}

const showError = (message) => {
  error.value = message
}

const clearError = () => {
  error.value = ''
}

// Provide methods to child components
const appMethods = {
  showLoading,
  hideLoading,
  showError,
  clearError
}

// Make methods available globally
window.appMethods = appMethods
</script>

<style scoped>
#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
</style>