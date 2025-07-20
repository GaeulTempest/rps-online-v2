<template>
  <div class="bg-white bg-opacity-10 backdrop-blur-md rounded-xl p-4">
    <div class="mb-4">
      <h3 class="text-lg font-bold text-white">{{ playerName }}</h3>
      <div v-if="isLocal && gesture !== 'none'" class="flex items-center mt-2">
        <span class="text-sm text-blue-200 mr-2">Detected:</span>
        <span class="text-white font-semibold">{{ gesture }}</span>
        <span class="text-xs text-blue-300 ml-2">({{ Math.round(confidence * 100) }}%)</span>
      </div>
    </div>

    <div class="relative bg-black rounded-lg overflow-hidden" style="aspect-ratio: 4/3;">
      <!-- Local video (camera) -->
      <video
        v-if="isLocal"
        ref="videoElement"
        autoplay
        muted
        playsinline
        class="w-full h-full object-cover"
        :class="{ 'scale-x-[-1]': isLocal }"
      ></video>

      <!-- Remote video (opponent stream) -->
      <img
        v-else-if="streamData"
        :src="`data:image/jpeg;base64,${streamData}`"
        class="w-full h-full object-cover"
        alt="Opponent video"
      />

      <!-- Placeholder -->
      <div
        v-else
        class="w-full h-full flex items-center justify-center text-white text-opacity-50"
      >
        <div class="text-center">
          <div class="text-6xl mb-4">📹</div>
          <p>{{ isLocal ? 'Starting camera...' : 'Waiting for opponent...' }}</p>
        </div>
      </div>

      <!-- Gesture overlay -->
      <div v-if="isLocal && gesture !== 'none'" class="absolute top-4 right-4">
        <div class="bg-black bg-opacity-70 text-white px-3 py-2 rounded-lg">
          <div class="text-2xl text-center mb-1">{{ getGestureEmoji(gesture) }}</div>
          <div class="text-xs text-center">{{ gesture }}</div>
        </div>
      </div>

      <!-- Connection status -->
      <div v-if="!isLocal && !streamData" class="absolute bottom-4 left-4">
        <div class="bg-red-600 bg-opacity-80 text-white px-3 py-1 rounded-lg text-sm">
          Connecting...
        </div>
      </div>
    </div>

    <!-- Canvas for frame capture (hidden) -->
    <canvas
      v-if="isLocal"
      ref="canvasElement"
      class="hidden"
      width="640"
      height="480"
    ></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { initializeCamera, captureFrame } from '../utils/camera.js'

const props = defineProps({
  isLocal: {
    type: Boolean,
    default: false
  },
  playerName: {
    type: String,
    default: 'Player'
  },
  gesture: {
    type: String,
    default: 'none'
  },
  confidence: {
    type: Number,
    default: 0
  },
  streamData: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['frame-captured'])

const videoElement = ref(null)
const canvasElement = ref(null)
const stream = ref(null)
const isCapturing = ref(false)

let captureInterval = null

onMounted(async () => {
  if (props.isLocal) {
    await setupLocalVideo()
  }
})

onUnmounted(() => {
  cleanup()
})

const setupLocalVideo = async () => {
  try {
    window.appMethods?.showLoading('Accessing camera...')
    
    const mediaStream = await initializeCamera()
    stream.value = mediaStream
    
    if (videoElement.value) {
      videoElement.value.srcObject = mediaStream
      
      // Wait for video to be ready
      await new Promise((resolve) => {
        videoElement.value.onloadedmetadata = resolve
      })
      
      // Start frame capture
      startFrameCapture()
    }
    
    window.appMethods?.hideLoading()
    
  } catch (error) {
    console.error('Error setting up camera:', error)
    window.appMethods?.hideLoading()
    
    let errorMessage = 'Failed to access camera. '
    if (error.name === 'NotAllowedError') {
      errorMessage += 'Please allow camera access and refresh the page.'
    } else if (error.name === 'NotFoundError') {
      errorMessage += 'No camera found on this device.'
    } else {
      errorMessage += 'Please check your camera permissions.'
    }
    
    window.appMethods?.showError(errorMessage)
  }
}

const startFrameCapture = () => {
  if (captureInterval) {
    clearInterval(captureInterval)
  }
  
  // Capture frames at 10 FPS for gesture detection
  captureInterval = setInterval(() => {
    if (videoElement.value && canvasElement.value && !isCapturing.value) {
      captureVideoFrame()
    }
  }, 100) // 100ms = 10 FPS
}

const captureVideoFrame = async () => {
  if (isCapturing.value) return
  
  isCapturing.value = true
  
  try {
    const frameData = captureFrame(videoElement.value, canvasElement.value)
    if (frameData) {
      emit('frame-captured', frameData)
    }
  } catch (error) {
    console.error('Error capturing frame:', error)
  } finally {
    isCapturing.value = false
  }
}

const cleanup = () => {
  if (captureInterval) {
    clearInterval(captureInterval)
    captureInterval = null
  }
  
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop())
    stream.value = null
  }
}

const getGestureEmoji = (gesture) => {
  const emojis = {
    rock: '✊',
    paper: '✋',
    scissors: '✌️',
    none: '❓'
  }
  return emojis[gesture] || '❓'
}

// Watch for stream data changes
watch(() => props.streamData, (newData) => {
  // Could add additional processing here if needed
})
</script>