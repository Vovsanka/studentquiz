<script setup lang="ts">
import { ref, reactive } from 'vue'
import axios from 'axios';

import { type Credentials, type UserInfo } from '@/types/UserTypes'
import { useSessionStore } from '@/stores/SessionStore'
import { BASE_URL } from '@/constants/constants';

const emit = defineEmits(["register", "login"]);

const session = useSessionStore()

const greetUser = (userInfo : UserInfo) => {
  return `Hello ${userInfo.name}! You are logged in.`
}

const message = ref(session.userInfo !== null ? greetUser(session.userInfo) : '');

const credentials = reactive({
  username: '',
  password: ''
} as Credentials)

const login = async (credentials: Credentials) => {
  let formData = new FormData()
  formData.append('credentials', JSON.stringify(credentials))
  console.log('Backend: ' + BASE_URL)
  await axios.request({
    method: 'POST',
    url: BASE_URL + '/frontend_api/get_token',
    data: formData,
    timeout: 10000
  })
    .then((response) => {
      const userInfo = response.data as UserInfo
      session.userInfo = userInfo
      message.value = greetUser(userInfo)
      credentials.username = ''
      credentials.password = ''
      session.setTokenRefresh()
      emit('login')
    })
    .catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log('Error: ' + errorMessage[0] + ' Reason: ' + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1])
    });
  showPageContent()
}

const logout = () => {
  session.userInfo = null
  message.value = ''
  showPageContent()
}

const pageContent = ref(null as null | HTMLElement);
const showPageContent = () => {
  (pageContent.value as HTMLElement).scrollIntoView({ behavior: "instant" });
};

defineExpose({ login })
</script>

<template>
  <form onsubmit="return false" class="user-data" ref="pageContent">
    <div class="user-data__set">
      <h2 class="page-title">Log in</h2>
      <button
        class="user-data__button btn btn-warning"
        type="button"
        @click="$emit('register')"
        v-if="session.userInfo === null"
      >
        Register
      </button>
    </div>
    <div class="user-data__item form-group" v-show="session.userInfo === null">
      <label for="login-username">Username</label>
      <input
        class="form-control"
        id="login-username"
        placeholder="Enter username"
        v-model="credentials.username"
      />
    </div>
    <div class="user-data__item form-group" v-show="session.userInfo === null">
      <label for="login-password">Password</label>
      <input
        type="password"
        class="form-control"
        id="login-password"
        placeholder="Enter password"
        v-model="credentials.password"
      />
    </div>
    <div class="user-data__set">
      <button
        v-show="session.userInfo === null"
        @click="login(credentials)"
        type="submit"
        class="user-data__button btn btn-primary"
      >
        Log-in
      </button>
      <button
        v-show="session.userInfo !== null"
        @click="logout()"
        type="reset"
        class="user-data__button btn btn-danger"
      >
        Log-out
      </button>
    </div>
    <p class="user-data__message">{{ message }}</p>
  </form>
</template>

<style scoped lang="scss">
@import "@/assets/styles/login.scss";
</style>
