/**
 * Camera utilities for accessing user media and capturing frames
 */

export const generatePlayerId = () => {
  return `player_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

export const initializeCamera = async (constraints = {}) => {
  const defaultConstraints = {
    video: {
      width: { ideal: 640 },
      height: { ideal: 480 },
      frameRate: { ideal: 30, max: 30 },
      facingMode: 'user'
    },
    audio: false
  }

  const finalConstraints = {
    ...defaultConstraints,
    ...constraints
  }

  try {
    // Check if getUserMedia is supported
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('getUserMedia is not supported in this browser')
    }

    // Request camera access
    const stream = await navigator.mediaDevices.getUserMedia(finalConstraints)
    
    console.log('Camera initialized successfully')
    return stream
    
  } catch (error) {
    console.error('Error initializing camera:', error)
    
    // Provide more specific error messages
    if (error.name === 'NotAllowedError') {
      throw new Error('Camera access denied. Please allow camera permissions.')
    } else if (error.name === 'NotFoundError') {
      throw new Error('No camera found on this device.')
    } else if (error.name === 'NotReadableError') {
      throw new Error('Camera is already in use by another application.')
    } else if (error.name === 'OverconstrainedError') {
      throw new Error('Camera does not meet the required specifications.')
    } else {
      throw new Error(`Camera error: ${error.message}`)
    }
  }
}

export const captureFrame = (videoElement, canvasElement, quality = 0.8) => {
  try {
    if (!videoElement || !canvasElement) {
      console.warn('Video or canvas element not provided')
      return null
    }

    // Check if video is ready
    if (videoElement.readyState !== videoElement.HAVE_ENOUGH_DATA) {
      return null
    }

    const canvas = canvasElement
    const ctx = canvas.getContext('2d')
    
    // Set canvas size to match video
    canvas.width = videoElement.videoWidth || 640
    canvas.height = videoElement.videoHeight || 480

    // Draw video frame to canvas
    ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height)

    // Convert to base64 with compression
    const dataURL = canvas.toDataURL('image/jpeg', quality)
    
    // Remove the data URL prefix to get just the base64 data
    const base64Data = dataURL.split(',')[1]
    
    return base64Data
    
  } catch (error) {
    console.error('Error capturing frame:', error)
    return null
  }
}

export const resizeFrame = (originalBase64, maxWidth = 320, maxHeight = 240, quality = 0.7) => {
  return new Promise((resolve) => {
    try {
      const img = new Image()
      
      img.onload = () => {
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')
        
        // Calculate new dimensions while maintaining aspect ratio
        let { width, height } = img
        
        if (width > maxWidth || height > maxHeight) {
          const ratio = Math.min(maxWidth / width, maxHeight / height)
          width *= ratio
          height *= ratio
        }
        
        canvas.width = width
        canvas.height = height
        
        // Draw resized image
        ctx.drawImage(img, 0, 0, width, height)
        
        // Convert to base64
        const resizedDataURL = canvas.toDataURL('image/jpeg', quality)
        const base64Data = resizedDataURL.split(',')[1]
        
        resolve(base64Data)
      }
      
      img.onerror = () => {
        console.error('Error loading image for resize')
        resolve(originalBase64) // Return original if resize fails
      }
      
      img.src = `data:image/jpeg;base64,${originalBase64}`
      
    } catch (error) {
      console.error('Error resizing frame:', error)
      resolve(originalBase64) // Return original if resize fails
    }
  })
}

export const stopCamera = (stream) => {
  if (stream) {
    stream.getTracks().forEach(track => {
      track.stop()
      console.log('Camera track stopped:', track.kind)
    })
  }
}

export const getCameraConstraints = (quality = 'medium') => {
  const constraints = {
    low: {
      video: {
        width: { ideal: 320 },
        height: { ideal: 240 },
        frameRate: { ideal: 15, max: 20 }
      }
    },
    medium: {
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        frameRate: { ideal: 30, max: 30 }
      }
    },
    high: {
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        frameRate: { ideal: 30, max: 30 }
      }
    }
  }

  return constraints[quality] || constraints.medium
}

export const checkCameraSupport = () => {
  const support = {
    getUserMedia: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
    mediaDevices: !!navigator.mediaDevices,
    webRTC: !!(window.RTCPeerConnection || window.webkitRTCPeerConnection || window.mozRTCPeerConnection)
  }

  console.log('Camera support check:', support)
  return support
}