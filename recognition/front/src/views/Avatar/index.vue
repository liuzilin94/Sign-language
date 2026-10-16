<template>
  <div class="avatar-page">
    <div class="page-header">
      <h2>数字人手语演示</h2>
      <p>输入文字，观看数字人手语动画</p>
    </div>
    
    <div class="avatar-container">
      <div class="input-section">
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="2"
          placeholder="请输入想要转换为手语的文字，如：你好、谢谢..."
          maxlength="50"
          show-word-limit
          @keydown.enter="handleInput"
        />
        <div class="input-actions">
          <el-button @click="clearInput" :disabled="!inputText">清空</el-button>
          <el-button type="primary" @click="handleInput" :loading="loading">
            <el-icon><VideoPlay /></el-icon>
            播放手语
          </el-button>
        </div>
      </div>
      
      <div class="preset-words">
        <span class="label">快捷词：</span>
        <div class="word-chips">
          <span
            v-for="word in presetWords"
            :key="word"
            class="word-chip"
            @click="selectWord(word)"
          >
            {{ word }}
          </span>
        </div>
      </div>
      
      <div class="display-section">
        <div class="avatar-view">
          <canvas ref="canvasRef" class="three-canvas"></canvas>
          
          <div class="loading-overlay" v-if="loading">
            <el-icon class="is-loading" style="font-size: 40px; color: #fff;"><Loading /></el-icon>
            <span>加载模型中...</span>
          </div>
          
          <div class="canvas-hint" v-if="!currentWord && !loading">
            <el-icon><InfoFilled /></el-icon>
            <span>输入文字后点击播放，或点击快捷词</span>
          </div>
          
          <div class="current-word-display" v-if="currentWord && !loading">
            <span class="word-text">{{ currentWord }}</span>
          </div>
        </div>
        
        <div class="control-bar">
          <div class="playback-controls">
            <el-button-group>
              <el-button :icon="isPlaying ? 'VideoPause' : 'VideoPlay'" @click="togglePlay">
                {{ isPlaying ? '暂停' : '播放' }}
              </el-button>
              <el-button icon="RefreshLeft" @click="replay">重播</el-button>
            </el-button-group>
          </div>
          
          <div class="speed-control">
            <span>速度：</span>
            <el-radio-group v-model="playbackSpeed" @change="changeSpeed">
              <el-radio-button :value="0.5">0.5x</el-radio-button>
              <el-radio-button :value="1">1x</el-radio-button>
              <el-radio-button :value="1.5">1.5x</el-radio-button>
            </el-radio-group>
          </div>
          
          <div class="bg-control">
            <span>背景：</span>
            <el-radio-group v-model="bgStyle" @change="changeBackground">
              <el-radio-button value="gradient">渐变</el-radio-button>
              <el-radio-button value="particles">粒子</el-radio-button>
              <el-radio-button value="orb">光球</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </div>
      
      <div class="animation-tips">
        <el-icon><InfoFilled /></el-icon>
        <span>操作提示：鼠标左键旋转 | 滚轮缩放 | 右键平移</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { VideoPlay, VideoPause, RefreshLeft, Loading, InfoFilled } from '@element-plus/icons-vue'

const canvasRef = ref(null)
const inputText = ref('')
const loading = ref(false)
const currentWord = ref('')
const isPlaying = ref(false)
const playbackSpeed = ref(1)
const bgStyle = ref('gradient')

const presetWords = ['你好', '谢谢', '早上好']

const modelMap = {
  '你好': 'niwo.glb',
  '我': 'niwo.glb',
  '谢谢': 'xiexie1.glb',
  '早上好': 'zaoshang.glb'
}

const defaultModel = 'initial.glb'

let threeInstance = null
let THREE = null
let GLTFLoader = null
let OrbitControls = null

async function initThree() {
  if (!canvasRef.value) return
  
  // 动态导入 Three.js
  if (!THREE) {
    THREE = await import('three')
    GLTFLoader = (await import('three/addons/loaders/GLTFLoader.js')).GLTFLoader
    OrbitControls = (await import('three/addons/controls/OrbitControls.js')).OrbitControls
  }
  
  const canvas = canvasRef.value
  
  // 确保 canvas 有尺寸
  const canvasWidth = canvas.offsetWidth || 800
  const canvasHeight = canvas.offsetHeight || 450
  
  const scene = new THREE.Scene()
  
  if (bgStyle.value === 'gradient') {
    scene.background = new THREE.Color(0x1a1a2e)
  } else if (bgStyle.value === 'particles') {
    scene.background = new THREE.Color(0x050510)
  } else {
    scene.background = new THREE.Color(0x0a0515)
  }
  
  const camera = new THREE.PerspectiveCamera(50, canvasWidth / canvasHeight, 0.1, 100)
  camera.position.set(0, 1.6, 2.0)
  
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true })
  renderer.setSize(canvasWidth, canvasHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 2.5
  
  const controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  controls.minDistance = 1
  controls.maxDistance = 10
  controls.target.set(0, 1.3, 0)
  controls.minPolarAngle = Math.PI * 0.12
  controls.maxPolarAngle = Math.PI * 0.52
  controls.update()
  
  const hemiLight = new THREE.HemisphereLight(0xb4c6e7, 0xc9b8a8, 1.2)
  scene.add(hemiLight)
  
  const ambientLight = new THREE.AmbientLight(0xfff8f0, 2.5)
  scene.add(ambientLight)
  
  const mainLight = new THREE.DirectionalLight(0xffffff, 2.5)
  mainLight.position.set(3, 5, 3)
  scene.add(mainLight)
  
  const fillLight = new THREE.DirectionalLight(0xe8d5c4, 1.5)
  fillLight.position.set(-2, 2, -2)
  scene.add(fillLight)
  
  const backLight = new THREE.DirectionalLight(0xffffff, 1.2)
  backLight.position.set(0, 3, -3)
  scene.add(backLight)
  
  const frontLight = new THREE.PointLight(0xfff5eb, 3.5, 8)
  frontLight.position.set(0, 1.6, 2.5)
  scene.add(frontLight)
  
  const sideLightLeft = new THREE.PointLight(0xfff5eb, 2.0, 6)
  sideLightLeft.position.set(-2, 1.5, 1)
  scene.add(sideLightLeft)
  
  const sideLightRight = new THREE.PointLight(0xfff5eb, 2.0, 6)
  sideLightRight.position.set(2, 1.5, 1)
  scene.add(sideLightRight)
  
  const groundGeometry = new THREE.CircleGeometry(3, 64)
  const groundMaterial = new THREE.MeshStandardMaterial({
    color: 0x5a5a7a,
    roughness: 0.8,
    metalness: 0.2
  })
  const ground = new THREE.Mesh(groundGeometry, groundMaterial)
  ground.rotation.x = -Math.PI / 2
  ground.receiveShadow = true
  scene.add(ground)
  
  const loader = new GLTFLoader()
  let mixer = null
  let mainAction = null
  let model = null
  const clock = new THREE.Clock()
  
  let bgParticles = null
  let bgOrbs = []
  
  function updateBackground() {
    if (bgParticles) {
      scene.remove(bgParticles)
      bgParticles = null
    }
    bgOrbs.forEach(orb => scene.remove(orb))
    bgOrbs = []
    
    if (bgStyle.value === 'gradient') {
      scene.background = new THREE.Color(0x1a1a2e)
    } else if (bgStyle.value === 'particles') {
      scene.background = new THREE.Color(0x050510)
      const geometry = new THREE.BufferGeometry()
      const count = 500
      const positions = new Float32Array(count * 3)
      for (let i = 0; i < count * 3; i++) {
        positions[i] = (Math.random() - 0.5) * 15
      }
      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
      const material = new THREE.PointsMaterial({
        color: 0x4ecdc4,
        size: 0.05,
        transparent: true,
        opacity: 0.8
      })
      bgParticles = new THREE.Points(geometry, material)
      scene.add(bgParticles)
    } else if (bgStyle.value === 'orb') {
      scene.background = new THREE.Color(0x0a0515)
      const colors = [0xff6b6b, 0x4ecdc4, 0xffe66d, 0x95e1d3, 0xf38181]
      for (let i = 0; i < 5; i++) {
        const geometry = new THREE.SphereGeometry(0.3 + Math.random() * 0.5, 32, 32)
        const material = new THREE.MeshBasicMaterial({
          color: colors[i],
          transparent: true,
          opacity: 0.3
        })
        const orb = new THREE.Mesh(geometry, material)
        orb.position.set(
          (Math.random() - 0.5) * 8,
          (Math.random() - 0.5) * 4 + 2,
          (Math.random() - 0.5) * 6 - 3
        )
        orb.userData = {
          speed: 0.005 + Math.random() * 0.01,
          offset: Math.random() * Math.PI * 2
        }
        scene.add(orb)
        bgOrbs.push(orb)
      }
    }
  }
  
  updateBackground()
  
  const defaultCamPos = new THREE.Vector3().copy(camera.position)
  const defaultTarget = new THREE.Vector3().copy(controls.target)
  
  function computeCharacterBox(object) {
    object.updateMatrixWorld(true)
    const box = new THREE.Box3()
    let has = false
    object.traverse((child) => {
      if (!child.isMesh || !child.geometry) return
      const geom = child.geometry
      if (!geom.boundingBox) geom.computeBoundingBox()
      const bb = geom.boundingBox
      if (!bb || bb.isEmpty()) return
      const transformed = bb.clone().applyMatrix4(child.matrixWorld)
      if (!has) {
        box.copy(transformed)
        has = true
      } else {
        box.union(transformed)
      }
    })
    if (!has) {
      box.setFromObject(object)
    }
    return box
  }
  
  function frameUpperBody(object) {
    const box = computeCharacterBox(object)
    if (box.isEmpty()) return
    const size = box.getSize(new THREE.Vector3())
    const min = box.min
    const max = box.max
    const cx = (min.x + max.x) * 0.5
    const cz = (min.z + max.z) * 0.5
    const focusY = min.y + size.y * 0.7
    const focus = new THREE.Vector3(cx, focusY, cz)
    const halfVisibleY = size.y * 0.42
    const fovRad = THREE.MathUtils.degToRad(camera.fov)
    const distForHeight = (halfVisibleY / Math.tan(fovRad / 2)) * 1.05
    const depth = Math.max(size.x, size.z) * 0.55
    const back = Math.max(distForHeight, depth, 0.35)
    const camY = focusY + size.y * 0.06
    camera.position.set(cx, camY, cz + back)
    controls.target.copy(focus)
    controls.minDistance = Math.max(size.y * 0.12, 0.25)
    controls.maxDistance = Math.max(size.y * 5, 8)
    controls.minPolarAngle = Math.PI * 0.12
    controls.maxPolarAngle = Math.PI * 0.52
    controls.update()
    defaultCamPos.copy(camera.position)
    defaultTarget.copy(focus)
  }
  
  function loadModel(modelFile, shouldFrame = false) {
    if (model) {
      scene.remove(model)
      model = null
    }
    if (mixer) {
      mixer.stopAllAction()
      mixer = null
      mainAction = null
    }
    
    loading.value = true
    console.log('开始加载模型:', modelFile)
    
    loader.load(
      modelFile,
      (gltf) => {
        console.log('模型加载成功', gltf)
        model = gltf.scene
        model.updateMatrixWorld(true)
        
        const box = computeCharacterBox(model)
        const center = box.getCenter(new THREE.Vector3())
        const size = box.getSize(new THREE.Vector3())
        
        const maxDim = Math.max(size.x, size.y, size.z)
        const scale = 1.5 / maxDim
        model.scale.setScalar(scale)
        
        model.position.x = -center.x * scale
        model.position.y = -box.min.y * scale
        model.position.z = -center.z * scale
        
        console.log('模型位置:', model.position.x, model.position.y, model.position.z)
        console.log('模型缩放:', scale)
        
        scene.add(model)
        console.log('场景中的对象数量:', scene.children.length)
        
        model.traverse((child) => {
          if (child.isMesh) {
            child.castShadow = true
            child.receiveShadow = true
          }
        })
        
        if (shouldFrame) {
          frameUpperBody(model)
        }
        
        if (gltf.animations && gltf.animations.length > 0) {
          mixer = new THREE.AnimationMixer(model)
          mainAction = mixer.clipAction(gltf.animations[0])
          mainAction.setLoop(THREE.LoopOnce)
          mainAction.clampWhenFinished = true
          mainAction.play()
          isPlaying.value = true
          
          mixer.addEventListener('finished', () => {
            loadModel(`/models/avatar/${defaultModel}`, false)
            isPlaying.value = false
          })
        }
        
        loading.value = false
      },
      (progress) => {
        console.log('加载进度:', Math.round(progress.loaded / progress.total * 100) + '%')
      },
      (error) => {
        console.error('加载失败:', error)
        loading.value = false
      }
    )
  }
  
  // 先初始化 threeInstance（至少要有 animationId）
  let animationId = null
  threeInstance = {
    renderer,
    controls,
    camera,
    loadModel,
    togglePlay: () => {
      if (mainAction && mixer) {
        if (isPlaying.value) {
          mixer.timeScale = 0
          isPlaying.value = false
        } else {
          mixer.timeScale = playbackSpeed.value
          mainAction.play()
          isPlaying.value = true
        }
      }
    },
    replay: () => {
      if (model) {
        loadModel(`/models/avatar/${currentWord.value && modelMap[currentWord.value] ? modelMap[currentWord.value] : defaultModel}`, false)
      }
    },
    resetCamera: () => {
      camera.position.copy(defaultCamPos)
      controls.target.copy(defaultTarget)
      controls.update()
    },
    changeBackground: () => {
      updateBackground()
    },
    dispose: () => {
      window.removeEventListener('resize', handleResize)
      if (animationId) {
        cancelAnimationFrame(animationId)
      }
      renderer.dispose()
    }
  }
  
  loadModel(`/models/avatar/${defaultModel}`, true)
  
  function animate() {
    animationId = requestAnimationFrame(animate)
    
    const delta = clock.getDelta()
    if (mixer) {
      mixer.update(delta * playbackSpeed.value)
    }
    
    if (bgParticles) {
      bgParticles.rotation.y += 0.0005
    }
    if (bgOrbs.length > 0) {
      const time = Date.now() * 0.001
      bgOrbs.forEach(orb => {
        orb.position.y += Math.sin(time * orb.userData.speed * 100 + orb.userData.offset) * 0.002
        orb.position.x += Math.cos(time * orb.userData.speed * 50 + orb.userData.offset) * 0.001
      })
    }
    
    controls.update()
    renderer.render(scene, camera)
  }
  animate()
  
  function handleResize() {
    const width = canvas.offsetWidth || 800
    const height = canvas.offsetHeight || 450
    camera.aspect = width / height
    camera.updateProjectionMatrix()
    renderer.setSize(width, height)
  }
  window.addEventListener('resize', handleResize)
}

function handleInput() {
  const word = inputText.value.trim()
  if (word) {
    selectWord(word)
  }
}

function selectWord(word) {
  if (!threeInstance) return
  
  currentWord.value = word
  const modelFile = modelMap[word] || defaultModel
  threeInstance.loadModel(`/models/avatar/${modelFile}`, true)
}

function clearInput() {
  inputText.value = ''
  currentWord.value = ''
}

function togglePlay() {
  if (threeInstance) {
    threeInstance.togglePlay()
  }
}

function replay() {
  if (threeInstance) {
    threeInstance.replay()
  }
}

function changeSpeed() {
  if (threeInstance && threeInstance.controls) {
    const { mixer } = threeInstance
    if (mixer) {
      mixer.timeScale = playbackSpeed.value
    }
  }
}

function changeBackground() {
  if (threeInstance) {
    threeInstance.changeBackground()
  }
}

onMounted(() => {
  nextTick(() => {
    initThree()
  })
})

onUnmounted(() => {
  if (threeInstance) {
    threeInstance.dispose()
  }
})
</script>

<style scoped lang="scss">
.avatar-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 130px);
  
  .page-header {
    text-align: center;
    margin-bottom: 24px;
    
    h2 {
      font-size: 24px;
      color: #333;
      margin-bottom: 8px;
    }
    
    p {
      color: #999;
      font-size: 14px;
      margin: 0;
    }
  }
  
  .avatar-container {
    .input-section {
      background: #fff;
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 16px;
      
      .input-actions {
        display: flex;
        justify-content: flex-end;
        gap: 12px;
        margin-top: 12px;
      }
    }
    
    .preset-words {
      display: flex;
      align-items: center;
      margin-bottom: 16px;
      flex-wrap: wrap;
      gap: 12px;
      
      .label {
        color: #999;
        font-size: 14px;
      }
      
      .word-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        
        .word-chip {
          padding: 6px 14px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: #fff;
          border-radius: 16px;
          font-size: 13px;
          cursor: pointer;
          transition: all 0.3s;
          
          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
          }
        }
      }
    }
    
    .display-section {
      background: #fff;
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 16px;
      
      .avatar-view {
        position: relative;
        height: 450px;
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 16px;
        background: #1a1a2e;
        
        .three-canvas {
          width: 100%;
          height: 100%;
          display: block;
        }
        
        .loading-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(26, 26, 46, 0.8);
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 12px;
          color: #fff;
          font-size: 14px;
        }
        
        .canvas-hint {
          position: absolute;
          bottom: 20px;
          left: 50%;
          transform: translateX(-50%);
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 10px 16px;
          background: rgba(0, 0, 0, 0.5);
          border-radius: 20px;
          color: rgba(255, 255, 255, 0.7);
          font-size: 13px;
        }
        
        .current-word-display {
          position: absolute;
          top: 20px;
          left: 50%;
          transform: translateX(-50%);
          padding: 8px 20px;
          background: rgba(78, 205, 196, 0.9);
          border-radius: 20px;
          
          .word-text {
            font-size: 20px;
            font-weight: bold;
            color: #fff;
          }
        }
      }
      
      .control-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        align-items: center;
        
        .playback-controls,
        .speed-control,
        .bg-control {
          display: flex;
          align-items: center;
          gap: 8px;
          
          span {
            color: #666;
            font-size: 14px;
          }
        }
      }
    }
    
    .animation-tips {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 16px;
      background: #f0f9ff;
      border-radius: 8px;
      font-size: 13px;
      color: #667eea;
    }
  }
}

@media (max-width: 768px) {
  .avatar-page {
    .avatar-container {
      .display-section {
        .control-bar {
          flex-direction: column;
          align-items: flex-start;
        }
      }
    }
  }
}
</style>
