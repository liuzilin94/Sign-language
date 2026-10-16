<template>
  <header class="navbar">
    <div class="nav-container">
      <div class="logo" @click="$router.push('/')">
        <span class="logo-icon">🖐</span>
        <span class="logo-text">掌言手语</span>
      </div>

      <nav class="nav-links" :class="{ mobile: isMobile }">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
        >
          {{ item.name }}
        </router-link>
      </nav>

      <div class="nav-actions">
        <el-badge :value="3" :hidden="!unreadCount">
          <el-icon @click="$router.push('/messages')"><Bell /></el-icon>
        </el-badge>
        <div class="user-avatar" @click="$router.push('/profile')">
          <img v-if="isLoggedIn" :src="defaultAvatar" alt="头像" />
          <span v-else @click="$router.push('/login')">登录</span>
        </div>
      </div>

      <div class="mobile-menu-btn" @click="showMobileMenu = !showMobileMenu">
        <el-icon><Menu /></el-icon>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/store'
import { Bell, Menu } from '@element-plus/icons-vue'

defineProps({
  showSearch: { type: Boolean, default: true }
})

const route = useRoute()
const userStore = useUserStore()

const defaultAvatar = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48Y2lyY2xlIGN4PSI1MCIgY3k9IjM1IiByPSIyNSIgZmlsbD0iI2Q0ZDRkNCIvPjxjaXJjbGUgY3g9IjUwIiBjeT0iNzUiIHI9IjMwIiBmaWxsPSIjZDRkNGQ0Ii8+PC9zdmc+'

const showMobileMenu = ref(false)
const unreadCount = ref(3)
const isMobile = ref(window.innerWidth < 768)

const isLoggedIn = computed(() => userStore.isLoggedIn)

const navItems = [
  { name: '首页', path: '/' },
  { name: '词典', path: '/dictionary' },
  { name: '背词练习', path: '/practice' },
  { name: '数字人', path: '/avatar' },
  { name: '数据大屏', path: '/data' },
  { name: '社区', path: '/community' },
  { name: '我的', path: '/profile' }
]

function isActive(path) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>

<style scoped lang="scss">
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);

  .nav-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
    height: 60px;
    display: flex;
    align-items: center;
    gap: 30px;

    .logo {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;

      .logo-icon { font-size: 28px; }
      .logo-text {
        font-size: 20px;
        font-weight: bold;
        color: #667eea;
      }
    }


    .nav-links {
      display: flex;
      gap: 24px;

      .nav-item {
        text-decoration: none;
        color: #666;
        font-size: 15px;
        padding: 6px 0;
        border-bottom: 2px solid transparent;
        transition: all 0.3s;

        &:hover, &.active {
          color: #667eea;
          border-color: #667eea;
        }
      }

      &.mobile {
        display: none;
      }
    }

    .nav-actions {
      display: flex;
      align-items: center;
      gap: 16px;

      .el-icon {
        font-size: 22px;
        cursor: pointer;
        color: #666;

        &:hover { color: #667eea; }
      }

      .user-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        overflow: hidden;
        cursor: pointer;

        img { width: 100%; height: 100%; object-fit: cover; }

        span {
          display: block;
          width: 100%;
          height: 100%;
          line-height: 36px;
          text-align: center;
          background: #667eea;
          color: #fff;
          font-size: 12px;
        }
      }
    }

    .mobile-menu-btn {
      display: none;
      font-size: 24px;
      cursor: pointer;
    }
  }
}

@media (max-width: 768px) {
  .navbar {
    .nav-container {
      .search-box, .nav-links { display: none; }
      .mobile-menu-btn { display: block; }
    }
  }
}
</style>
