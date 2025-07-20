<template>
  <div class="max-w-2xl mx-auto">
    <div class="bg-white bg-opacity-10 backdrop-blur-md rounded-xl p-8 shadow-2xl">
      <div class="text-center mb-8">
        <div class="text-6xl mb-4">🎮</div>
        <h2 class="text-3xl font-bold text-white mb-2">Welcome to RPS Online!</h2>
        <p class="text-blue-200">Challenge friends to a real-time Rock Paper Scissors battle</p>
      </div>

      <div class="grid md:grid-cols-2 gap-6">
        <!-- Create Room -->
        <div class="bg-white bg-opacity-20 rounded-lg p-6">
          <h3 class="text-xl font-bold text-white mb-4 flex items-center">
            <span class="mr-2">🏠</span>
            Create Room
          </h3>
          <p class="text-blue-200 mb-6">Start a new game and invite a friend</p>
          <button 
            @click="createRoom"
            :disabled="isCreating"
            class="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-500 text-white font-bold py-3 px-6 rounded-lg transition-colors duration-200"
          >
            <span v-if="!isCreating">Create New Room</span>
            <span v-else class="flex items-center justify-center">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Creating...
            </span>
          </button>
        </div>

        <!-- Join Room -->
        <div class="bg-white bg-opacity-20 rounded-lg p-6">
          <h3 class="text-xl font-bold text-white mb-4 flex items-center">
            <span class="mr-2">🔗</span>
            Join Room
          </h3>
          <p class="text-blue-200 mb-4">Enter a room ID to join an existing game</p>
          <div class="space-y-4">
            <input
              v-model="joinRoomId"
              type="text"
              placeholder="Enter Room ID"
              class="w-full px-4 py-3 rounded-lg bg-white bg-opacity-20 border border-white border-opacity-30 text-white placeholder-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400"
              @keyup.enter="joinRoom"
              maxlength="8"
            >
            <button 
              @click="joinRoom"
              :disabled="!joinRoomId.trim() || isJoining"
              class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-500 text-white font-bold py-3 px-6 rounded-lg transition-colors duration-200"
            >
              <span v-if="!isJoining">Join Room</span>
              <span v-else class="flex items-center justify-center">
                <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Joining...
              </span>
            </button>
          </div>
        </div>
      </div>

      <!-- Instructions -->
      <div class="mt-8 bg-white bg-opacity-10 rounded-lg p-6">
        <h3 class="text-lg font-bold text-white mb-4">📋 How to Play</h3>
        <ul class="text-blue-200 space-y-2">
          <li class="flex items-start">
            <span class="mr-2">1.</span>
            <span>Allow camera access when prompted</span>
          </li>
          <li class="flex items-start">
            <span class="mr-2">2.</span>
            <span>Use hand gestures: ✊ Rock, ✋ Paper, ✌️ Scissors</span>
          </li>
          <li class="flex items-start">
            <span class="mr-2">3.</span>
            <span>Wait for countdown, then show your move!</span>
          </li>
          <li class="flex items-start">
            <span class="mr-2">4.</span>
            <span>First to 5 points wins the game</span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { createRoom as apiCreateRoom, getRoomStatus } from '../services/api.js'

const emit = defineEmits(['join-game'])

const joinRoomId = ref('')
const isCreating = ref(false)
const isJoining = ref(false)

const createRoom = async () => {
  if (isCreating.value) return

  isCreating.value = true
  
  try {
    window.appMethods?.showLoading('Creating room...')
    
    const response = await apiCreateRoom()
    const roomId = response.room_id
    
    window.appMethods?.hideLoading()
    
    // Join the created room
    emit('join-game', { roomId })
    
  } catch (error) {
    console.error('Error creating room:', error)
    window.appMethods?.hideLoading()
    window.appMethods?.showError('Failed to create room. Please try again.')
  } finally {
    isCreating.value = false
  }
}

const joinRoom = async () => {
  if (!joinRoomId.value.trim() || isJoining.value) return

  isJoining.value = true
  const roomId = joinRoomId.value.trim().toUpperCase()

  try {
    window.appMethods?.showLoading('Checking room...')
    
    // Check if room exists and is available
    const roomStatus = await getRoomStatus(roomId)
    
    if (roomStatus.players_count >= roomStatus.max_players) {
      throw new Error('Room is full')
    }
    
    window.appMethods?.hideLoading()
    
    // Join the room
    emit('join-game', { roomId })
    
  } catch (error) {
    console.error('Error joining room:', error)
    window.appMethods?.hideLoading()
    
    let errorMessage = 'Failed to join room.'
    if (error.response?.status === 404) {
      errorMessage = 'Room not found. Please check the Room ID.'
    } else if (error.message === 'Room is full') {
      errorMessage = 'This room is already full (2/2 players).'
    }
    
    window.appMethods?.showError(errorMessage)
  } finally {
    isJoining.value = false
  }
}
</script>