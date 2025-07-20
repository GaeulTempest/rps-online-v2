<template>
  <div class="bg-white bg-opacity-10 backdrop-blur-md rounded-xl p-6">
    <h3 class="text-xl font-bold text-white text-center mb-6">🏆 Scoreboard</h3>
    
    <div v-if="Object.keys(scores).length === 0" class="text-center text-blue-200">
      <p>Game hasn't started yet</p>
    </div>
    
    <div v-else class="grid grid-cols-3 gap-4 items-center">
      <!-- Player 1 -->
      <div class="text-center">
        <div class="bg-white bg-opacity-20 rounded-lg p-4">
          <div class="text-2xl font-bold text-white mb-2">{{ getPlayerScore(0) }}</div>
          <div class="text-sm text-blue-200">{{ getPlayerName(0) }}</div>
        </div>
      </div>
      
      <!-- VS -->
      <div class="text-center">
        <div class="text-3xl font-bold text-white">VS</div>
        <div class="text-sm text-blue-200 mt-2">First to 5 wins</div>
      </div>
      
      <!-- Player 2 -->
      <div class="text-center">
        <div class="bg-white bg-opacity-20 rounded-lg p-4">
          <div class="text-2xl font-bold text-white mb-2">{{ getPlayerScore(1) }}</div>
          <div class="text-sm text-blue-200">{{ getPlayerName(1) }}</div>
        </div>
      </div>
    </div>
    
    <!-- Game Progress -->
    <div v-if="Object.keys(scores).length > 0" class="mt-6">
      <div class="flex justify-between text-xs text-blue-200 mb-2">
        <span>{{ getPlayerName(0) }}</span>
        <span>{{ getPlayerName(1) }}</span>
      </div>
      <div class="w-full bg-white bg-opacity-20 rounded-full h-2">
        <div 
          class="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full transition-all duration-500"
          :style="{ width: `${getProgressPercentage()}%` }"
        ></div>
      </div>
      <div class="text-center text-xs text-blue-200 mt-2">
        Progress to Victory
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  scores: {
    type: Object,
    default: () => ({})
  },
  playerNames: {
    type: Object,
    default: () => ({})
  }
})

const playerIds = computed(() => Object.keys(props.scores))

const getPlayerScore = (index) => {
  const playerId = playerIds.value[index]
  return playerId ? props.scores[playerId] || 0 : 0
}

const getPlayerName = (index) => {
  const playerId = playerIds.value[index]
  if (!playerId) return index === 0 ? 'Player 1' : 'Player 2'
  
  return props.playerNames[playerId] || `Player ${index + 1}`
}

const getProgressPercentage = () => {
  if (playerIds.value.length < 2) return 0
  
  const score1 = getPlayerScore(0)
  const score2 = getPlayerScore(1)
  const maxScore = Math.max(score1, score2)
  
  if (maxScore === 0) return 0
  
  // Progress towards victory (5 points)
  return (maxScore / 5) * 100
}
</script>