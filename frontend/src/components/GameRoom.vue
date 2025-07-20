<template>
  <div class="max-w-6xl mx-auto">
    <!-- Header with Room Info -->
    <div class="bg-white bg-opacity-10 backdrop-blur-md rounded-xl p-4 mb-6">
      <div class="flex justify-between items-center">
        <div>
          <h2 class="text-2xl font-bold text-white">Room: {{ roomId }}</h2>
          <p class="text-blue-200">Players: {{ playersCount }}/2</p>
        </div>
        <div class="flex gap-4">
          <button 
            @click="restartGame"
            v-if="gameState === 'finished' || gameState === 'playing'"
            class="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            🔄 Restart
          </button>
          <button 
            @click="leaveGame"
            class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            🚪 Leave
          </button>
        </div>
      </div>
    </div>

    <!-- Game Status -->
    <div class="text-center mb-6">
      <div v-if="gameMessage" class="bg-white bg-opacity-20 rounded-lg p-4 mb-4">
        <p class="text-2xl font-bold text-white">{{ gameMessage }}</p>
      </div>
      
      <!-- Countdown -->
      <div v-if="countdown > 0" class="text-6xl font-bold text-yellow-400 animate-pulse">
        {{ countdown }}
      </div>
    </div>

    <!-- Score Board -->
    <ScoreBoard :scores="scores" :player-names="playerNames" class="mb-6" />

    <!-- Video Streams and Game Area -->
    <div class="grid md:grid-cols-2 gap-6 mb-6">
      <!-- Your Video -->
      <VideoStream
        ref="localVideoStream"
        :is-local="true"
        :player-name="`You (${playerId})`"
        :gesture="currentGesture"
        :confidence="gestureConfidence"
        @frame-captured="handleFrameCaptured"
      />

      <!-- Opponent Video -->
      <VideoStream
        :is-local="false"
        :player-name="opponentName"
        :stream-data="opponentVideoFrame"
      />
    </div>

    <!-- Game Controls -->
    <div class="text-center">
      <div v-if="gameState === 'waiting'" class="bg-white bg-opacity-20 rounded-lg p-6">
        <p class="text-xl text-white mb-4">Waiting for another player to join...</p>
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto"></div>
      </div>

      <div v-else-if="gameState === 'starting'" class="bg-white bg-opacity-20 rounded-lg p-6">
        <p class="text-xl text-white mb-4">Get ready to play!</p>
        <button 
          @click="setReady"
          :disabled="isReady"
          class="bg-green-600 hover:bg-green-700 disabled:bg-gray-500 text-white px-8 py-3 rounded-lg font-bold transition-colors"
        >
          {{ isReady ? '✅ Ready!' : '🎯 Ready' }}
        </button>
      </div>

      <div v-else-if="gameState === 'playing'" class="bg-white bg-opacity-20 rounded-lg p-6">
        <p class="text-xl text-white mb-4">Show your move with hand gesture!</p>
        <div class="flex justify-center items-center space-x-8">
          <div class="text-center">
            <div class="text-4xl mb-2">✊</div>
            <p class="text-white">Rock</p>
          </div>
          <div class="text-center">
            <div class="text-4xl mb-2">✋</div>
            <p class="text-white">Paper</p>
          </div>
          <div class="text-center">
            <div class="text-4xl mb-2">✌️</div>
            <p class="text-white">Scissors</p>
          </div>
        </div>
      </div>

      <div v-else-if="gameState === 'finished'" class="bg-white bg-opacity-20 rounded-lg p-6">
        <p class="text-2xl font-bold text-white mb-4">🎉 Game Finished!</p>
        <p class="text-xl text-white mb-4">{{ gameWinner ? `${gameWinner} wins!` : 'It\'s a draw!' }}</p>
        <button 
          @click="restartGame"
          class="bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-lg font-bold transition-colors"
        >
          🔄 Play Again
        </button>
      </div>
    </div>

    <!-- Round Result Modal -->
    <div v-if="showRoundResult" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-8 max-w-md mx-4 text-center">
        <h3 class="text-2xl font-bold mb-4">Round Result</h3>
        <div class="flex justify-center items-center space-x-8 mb-6">
          <div class="text-center">
            <p class="font-semibold mb-2">You</p>
            <div class="text-4xl">{{ getMoveEmoji(roundResult?.moves?.[playerId]) }}</div>
            <p class="text-sm text-gray-600">{{ roundResult?.moves?.[playerId] }}</p>
          </div>
          <div class="text-2xl">VS</div>
          <div class="text-center">
            <p class="font-semibold mb-2">Opponent</p>
            <div class="text-4xl">{{ getMoveEmoji(getOpponentMove()) }}</div>
            <p class="text-sm text-gray-600">{{ getOpponentMove() }}</p>
          </div>
        </div>
        <p class="text-xl font-bold mb-4">
          {{ getRoundResultText() }}
        </p>
        <button 
          @click="closeRoundResult"
          class="bg-blue-600 text-white py-2 px-6 rounded hover:bg-blue-700 transition-colors"
        >
          Continue
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import VideoStream from './VideoStream.vue'
import ScoreBoard from './ScoreBoard.vue'
import { WebSocketService } from '../services/websocket.js'

const props = defineProps({
  roomId: String,
  playerId: String
})

const emit = defineEmits(['leave-game'])

// Reactive state
const playersCount = ref(1)
const gameState = ref('waiting')
const gameMessage = ref('')
const countdown = ref(0)
const scores = ref({})
const currentGesture = ref('none')
const gestureConfidence = ref(0)
const isReady = ref(false)
const opponentVideoFrame = ref(null)
const opponentName = ref('Opponent')
const showRoundResult = ref(false)
const roundResult = ref(null)
const gameWinner = ref('')

// WebSocket instance
let wsService = null
const localVideoStream = ref(null)

// Computed
const playerNames = computed(() => {
  const names = {}
  names[props.playerId] = 'You'
  
  // Find opponent name
  Object.keys(scores.value).forEach(id => {
    if (id !== props.playerId) {
      names[id] = 'Opponent'
    }
  })
  
  return names
})

onMounted(async () => {
  try {
    // Initialize WebSocket connection
    wsService = new WebSocketService(props.roomId, props.playerId)
    
    // Setup WebSocket event handlers
    wsService.on('player_joined', handlePlayerJoined)
    wsService.on('player_left', handlePlayerLeft)
    wsService.on('game_start', handleGameStart)
    wsService.on('countdown', handleCountdown)
    wsService.on('round_start', handleRoundStart)
    wsService.on('gesture_detected', handleGestureDetected)
    wsService.on('opponent_frame', handleOpponentFrame)
    wsService.on('round_result', handleRoundResult)
    wsService.on('next_round', handleNextRound)
    wsService.on('game_end', handleGameEnd)
    wsService.on('game_restarted', handleGameRestarted)
    wsService.on('error', handleError)
    
    // Connect to WebSocket
    await wsService.connect()
    
  } catch (error) {
    console.error('Failed to initialize game:', error)
    window.appMethods?.showError('Failed to connect to game. Please try again.')
  }
})

onUnmounted(() => {
  if (wsService) {
    wsService.disconnect()
  }
})

// WebSocket event handlers
const handlePlayerJoined = (data) => {
  playersCount.value = data.players_count
  gameMessage.value = `Player joined (${data.players_count}/2)`
}

const handlePlayerLeft = (data) => {
  playersCount.value = data.players_count
  gameMessage.value = 'Player left the game'
  gameState.value = 'waiting'
}

const handleGameStart = (data) => {
  gameState.value = 'starting'
  gameMessage.value = data.message
}

const handleCountdown = (data) => {
  countdown.value = data.count
}

const handleRoundStart = (data) => {
  gameState.value = 'playing'
  gameMessage.value = data.message
  countdown.value = 0
  isReady.value = false
}

const handleGestureDetected = (data) => {
  currentGesture.value = data.gesture
  gestureConfidence.value = data.confidence
}

const handleOpponentFrame = (data) => {
  if (data.player_id !== props.playerId) {
    opponentVideoFrame.value = data.frame
  }
}

const handleRoundResult = (data) => {
  roundResult.value = data
  scores.value = data.scores
  showRoundResult.value = true
  gameState.value = 'result'
}

const handleNextRound = (data) => {
  gameMessage.value = data.message
  closeRoundResult()
}

const handleGameEnd = (data) => {
  gameState.value = 'finished'
  gameWinner.value = playerNames.value[data.winner] || data.winner
  scores.value = data.final_scores
}

const handleGameRestarted = (data) => {
  gameState.value = 'starting'
  gameMessage.value = data.message
  scores.value = {}
  isReady.value = false
  gameWinner.value = ''
}

const handleError = (data) => {
  window.appMethods?.showError(data.message)
}

// Game actions
const setReady = () => {
  if (isReady.value) return
  
  isReady.value = true
  wsService.send({
    type: 'player_ready'
  })
}

const restartGame = () => {
  wsService.send({
    type: 'restart_game'
  })
}

const leaveGame = () => {
  if (wsService) {
    wsService.disconnect()
  }
  emit('leave-game')
}

const handleFrameCaptured = (frameData) => {
  if (wsService && gameState.value === 'playing') {
    wsService.send({
      type: 'video_frame',
      frame: frameData
    })
  }
}

// Helper methods
const getMoveEmoji = (move) => {
  const emojis = {
    rock: '✊',
    paper: '✋',
    scissors: '✌️',
    none: '❌'
  }
  return emojis[move] || '❓'
}

const getOpponentMove = () => {
  if (!roundResult.value?.moves) return 'none'
  
  const moves = roundResult.value.moves
  const opponentId = Object.keys(moves).find(id => id !== props.playerId)
  return moves[opponentId] || 'none'
}

const getRoundResultText = () => {
  if (!roundResult.value) return ''
  
  const result = roundResult.value.result
  const winner = roundResult.value.winner
  
  if (result === 'draw') return "It's a draw!"
  if (winner === props.playerId) return "You win this round!"
  return "Opponent wins this round!"
}

const closeRoundResult = () => {
  showRoundResult.value = false
  roundResult.value = null
}
</script>