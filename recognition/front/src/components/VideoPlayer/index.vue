<template>
  <div class="video-player">
    <video
      ref="videoRef"
      :src="src"
      :poster="poster"
      @play="onPlay"
      @pause="onPause"
      @ended="onEnded"
      @timeupdate="onTimeUpdate"
      @loadedmetadata="onLoadedMetadata"
    ></video>
    <div class="controls" :class="{ show: showControls }">
      <div class="progress-bar" @click="seek">
        <div class="progress" :style="{ width: progress + '%' }"></div>
      </div>
      <div class="buttons">
        <el-icon @click="togglePlay"><VideoPlay v-if="!isPlaying" /><VideoPause v-else /></el-icon>
        <span class="time">{{ formatTime(currentTime) }} / {{ formatTime(duration) }}</span>
        <el-select v-model="playbackRate" size="small" @change="changeRate">
          <el-option :value="0.5" label="0.5x" />
          <el-option :value="0.75" label="0.75x" />
          <el-option :value="1" label="1x" />
          <el-option :value="1.25" label="1.25x" />
          <el-option :value="1.5" label="1.5x" />
          <el-option :value="2" label="2x" />
        </el-select>
        <el-icon @click="toggleFullscreen"><FullScreen /></el-icon>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { VideoPlay, VideoPause, FullScreen } from '@element-plus/icons-vue'

const props = defineProps({
  src: { type: String, default: '' },
  poster: { type: String, default: '' },
  autoplay: { type: Boolean, default: false }
})

const emit = defineEmits(['play', 'pause', 'ended', 'timeupdate'])

const videoRef = ref(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const playbackRate = ref(1)
const showControls = ref(true)

const progress = computed(() => duration.value ? (currentTime.value / duration.value) * 100 : 0)

function togglePlay() {
  if (videoRef.value.paused) {
    videoRef.value.play()
  } else {
    videoRef.value.pause()
  }
}

function changeRate(rate) {
  videoRef.value.playbackRate = rate
}

function toggleFullscreen() {
  if (document.fullscreenElement) {
    document.exitFullscreen()
  } else {
    videoRef.value.parentElement.requestFullscreen()
  }
}

function seek(e) {
  const rect = e.target.getBoundingClientRect()
  const percent = (e.clientX - rect.left) / rect.width
  videoRef.value.currentTime = percent * duration.value
}

function formatTime(seconds) {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

function onPlay() { isPlaying.value = true; emit('play') }
function onPause() { isPlaying.value = false; emit('pause') }
function onEnded() { emit('ended') }
function onTimeUpdate() { currentTime.value = videoRef.value.currentTime; emit('timeupdate', currentTime.value) }
function onLoadedMetadata() { duration.value = videoRef.value.duration }
</script>

<style scoped lang="scss">
.video-player {
  position: relative;
  width: 100%;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  
  video {
    width: 100%;
    display: block;
  }
  
  .controls {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(transparent, rgba(0,0,0,0.8));
    padding: 8px;
    opacity: 0;
    transition: opacity 0.3s;
    
    &.show { opacity: 1; }
    
    .progress-bar {
      height: 4px;
      background: rgba(255,255,255,0.3);
      border-radius: 2px;
      cursor: pointer;
      margin-bottom: 8px;
      
      .progress {
        height: 100%;
        background: #409eff;
        border-radius: 2px;
        transition: width 0.1s;
      }
    }
    
    .buttons {
      display: flex;
      align-items: center;
      gap: 12px;
      
      .el-icon {
        color: #fff;
        font-size: 20px;
        cursor: pointer;
      }
      
      .time {
        color: #fff;
        font-size: 12px;
      }
      
      .el-select {
        width: 70px;
        
        .el-input__wrapper {
          background: transparent;
        }
      }
    }
  }
  
  &:hover .controls { opacity: 1; }
}
</style>
