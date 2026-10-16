<template>
  <header class="navbar">
    <div class="nav-inner">
      <router-link to="/" class="logo">
        <img src="/images/logo.png" alt="掌言" class="logo-img" />
        <span class="logo-text">掌言</span>
      </router-link>

      <nav class="nav-links" :class="{ open: mobileMenuOpen }">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
          @click="mobileMenuOpen = false"
        >
          <template v-if="item.icon">
            <el-icon class="nav-icon"><component :is="item.icon" /></el-icon>
          </template>
          {{ item.name }}
        </router-link>
      </nav>

      <div class="nav-actions">
        <router-link to="/messages" class="nav-icon-btn" title="消息">
          <el-badge :value="unreadCount" :hidden="!unreadCount" :max="9">
            <el-icon><Bell /></el-icon>
          </el-badge>
        </router-link>

        <el-dropdown trigger="click" @command="handleCommand" v-if="isLoggedIn">
          <div class="avatar-wrapper">
            <img v-if="userStore.userInfo?.avatar" :src="userStore.userInfo.avatar" alt="avatar" class="avatar" />
            <div v-else class="avatar avatar-placeholder">
              {{ userStore.userInfo?.username?.charAt(0) || 'U' }}
            </div>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon> 个人中心
              </el-dropdown-item>
              <el-dropdown-item command="settings">
                <el-icon><Setting /></el-icon> 设置
              </el-dropdown-item>
              <el-dropdown-item command="logout" divided>
                <el-icon><SwitchButton /></el-icon> 退出
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <router-link v-else to="/login" class="nav-login-btn">
          登录
        </router-link>

        <button class="mobile-toggle" @click="mobileMenuOpen = !mobileMenuOpen" aria-label="菜单">
          <el-icon><component :is="mobileMenuOpen ? 'Close' : 'Menu'" /></el-icon>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import {
  Bell, User, Setting, SwitchButton, Menu, Close,
  HomeFilled, Document, VideoPlay, ChatDotSquare,
  DataLine, UserFilled, Tools, VideoCamera,
  Promotion
} from '@element-plus/icons-vue'
import { useUserStore } from '@/store'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const mobileMenuOpen = ref(false)
const unreadCount = ref(0)

const isLoggedIn = computed(() => userStore.isLoggedIn)

const navItems = computed(() => {
  const items = [
    { name: '首页', path: '/', icon: HomeFilled },
    { name: '词典', path: '/dictionary', icon: Document },
    { name: '学习', path: '/learning', icon: VideoPlay },
    { name: '数字人', path: '/avatar', icon: VideoCamera },
    { name: '科普', path: '/science', icon: Promotion },
    { name: '社区', path: '/community', icon: UserFilled },
    { name: '数据中心', path: '/data', icon: DataLine },
  ]
  if (userStore.userInfo?.role === 'admin') {
    items.splice(7, 0, { name: '管理', path: '/admin', icon: Tools })
  }
  return items
})

function isActive(path) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

function handleCommand(cmd) {
  if (cmd === 'profile') router.push('/profile')
  else if (cmd === 'settings') router.push('/settings')
  else if (cmd === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info',
    }).then(() => {
      userStore.logout()
      router.push('/')
    }).catch(() => {})
  }
}
</script>

<style scoped lang="scss">
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(250, 250, 248, 0.94);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid #eaeaea;

  .nav-inner {
    max-width: 1100px;
    margin: 0 auto;
    padding: 0 32px;
    height: 60px;
    display: flex;
    align-items: center;
    gap: 32px;
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 10px;
    text-decoration: none;
    flex-shrink: 0;

    .logo-img {
      height: 28px;
      width: auto;
    }

    .logo-text {
      font-size: 16px;
      font-weight: 600;
      color: #0d0d0d;
      letter-spacing: 0.3px;
    }
  }

  .nav-links {
    display: flex;
    align-items: center;
    gap: 2px;
    flex: 1;

    .nav-item {
      display: flex;
      align-items: center;
      gap: 5px;
      font-size: 14px;
      font-weight: 450;
      color: #8a8a8a;
      text-decoration: none;
      padding: 6px 12px;
      border-radius: 6px;
      transition: all 180ms ease;
      white-space: nowrap;

      .nav-icon {
        font-size: 14px;
        opacity: 0.6;
      }

      &:hover {
        color: #0d0d0d;
        background: #f0f0ee;

        .nav-icon {
          opacity: 1;
        }
      }

      &.active {
        color: #0d0d0d;
        font-weight: 500;

        .nav-icon {
          opacity: 1;
        }
      }
    }
  }

  .nav-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;

    .nav-icon-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 6px;
      border-radius: 6px;
      color: #8a8a8a;
      text-decoration: none;
      transition: all 180ms ease;

      &:hover {
        color: #0d0d0d;
        background: #f0f0ee;
      }

      .el-icon {
        font-size: 18px;
      }
    }

    .avatar-wrapper {
      cursor: pointer;
      border-radius: 50%;
      overflow: hidden;
      width: 34px;
      height: 34px;
      border: 1px solid #eaeaea;
      transition: border-color 180ms ease;

      &:hover {
        border-color: #c8c8c8;
      }

      .avatar {
        width: 100%;
        height: 100%;
        object-fit: cover;

        &.avatar-placeholder {
          background: #0d0d0d;
          color: #fff;
          font-size: 13px;
          font-weight: 500;
          display: flex;
          align-items: center;
          justify-content: center;
        }
      }
    }

    .nav-login-btn {
      font-size: 14px;
      font-weight: 450;
      color: #0d0d0d;
      text-decoration: none;
      padding: 6px 16px;
      border: 1px solid #e0e0e0;
      border-radius: 6px;
      transition: all 180ms ease;

      &:hover {
        background: #0d0d0d;
        color: #fff;
        border-color: #0d0d0d;
      }
    }

    .mobile-toggle {
      display: none;
      padding: 6px;
      border-radius: 6px;
      color: #3a3a3a;
      transition: background 180ms ease;

      &:hover {
        background: #f0f0ee;
      }
    }
  }
}

@media (max-width: 768px) {
  .navbar .nav-inner {
    padding: 0 20px;
    gap: 12px;
  }

  .navbar .nav-links {
    display: none;
    position: fixed;
    top: 60px;
    left: 0;
    right: 0;
    background: rgba(250, 250, 248, 0.98);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid #eaeaea;
    flex-direction: column;
    padding: 12px 16px;
    gap: 2px;

    &.open {
      display: flex;
    }

    .nav-item {
      width: 100%;
      padding: 11px 14px;
      font-size: 15px;
    }
  }

  .navbar .nav-actions {
    .nav-icon-btn {
      display: none;
    }

    .mobile-toggle {
      display: flex;
    }
  }
}
</style>
