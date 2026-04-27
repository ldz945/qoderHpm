<template>
  <div class="login-container">
    <div class="login-card">
      <h2 style="text-align:center; margin-bottom:32px">HPM 项目管理系统</h2>
      <a-form :model="form" @finish="handleLogin" layout="vertical">
        <a-form-item label="用户名" name="username" :rules="[{required:true,message:'请输入用户名'}]">
          <a-input v-model:value="form.username" size="large" placeholder="请输入用户名" />
        </a-form-item>
        <a-form-item label="密码" name="password" :rules="[{required:true,message:'请输入密码'}]">
          <a-input-password v-model:value="form.password" size="large" placeholder="请输入密码" @pressEnter="handleLogin" />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" size="large" block :loading="loading">登 录</a-button>
        </a-form-item>
      </a-form>
      <div style="text-align:center;color:#999;font-size:12px">默认账号: admin / hpm123456</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import axios from 'axios'

const router = useRouter()
const loading = ref(false)
const form = ref({ username: '', password: '' })

const handleLogin = async () => {
  loading.value = true
  try {
    // Call login API directly (no interceptor needed for login)
    const res = await axios.post('/api/auth/login/', {
      username: form.value.username,
      password: form.value.password,
    })
    const { access, refresh } = res.data
    localStorage.setItem('hpm_token', access)
    localStorage.setItem('hpm_refresh_token', refresh)

    // Fetch current user info
    const userRes = await axios.get('/api/auth/me/', {
      headers: { Authorization: `Bearer ${access}` }
    })
    const user = userRes.data
    localStorage.setItem('hpm_user', JSON.stringify(user))
    localStorage.setItem('hpm_role', (user.roles || []).join(','))

    message.success(`欢迎, ${user.name}`)
    router.push('/')
  } catch (e) {
    const detail = e.response?.data?.detail || '登录失败，请检查用户名和密码'
    message.error(detail)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}
</style>

