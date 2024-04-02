<script setup lang="ts">
import { ref, reactive, toRaw } from 'vue'
import axios from 'axios';

import { Role, type User, type UserInfo, type Credentials } from '@/types/UserTypes'
import { useSessionStore } from '@/stores/SessionStore'
import { BASE_URL } from '@/constants/constants'

const emit = defineEmits(['login'])

const session = useSessionStore()

const user = reactive({
  info: {
    username: '',
    name: '',
    role: Role.STUDENT,
    token: ''
  } as UserInfo,
  credentials: {
    username: '',
    password: ''
  } as Credentials
} as User)

const passwordRepeat = ref('')


const register = async () => {
  // TODO: query backend with user
  // TODO: additional fields for student / teacher
  if (user.credentials.password === passwordRepeat.value) {
    user.info.username = user.credentials.username
    let formData = new FormData()
    formData.append('user', JSON.stringify(user))
    await axios.request({
      method: 'POST',
      url: BASE_URL + '/frontend_api/register_user',
      data: formData,
      timeout: 10000
    }).then((response) => {

      user.info =  {
        username: '',
        name: '',
        role: Role.STUDENT,
        token: ''
      } as UserInfo
      const credentials = toRaw(user.credentials)
      user.credentials = {
        username: '',
        password: ''
      } as Credentials
      passwordRepeat.value = ''
      console.log('User created!')
      emit('login', credentials)
    }).catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log('Error: ' + errorMessage[0] + ' Reason: ' + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1])
    });
  } else {
    alert('Error: passwords are not the same!')
    user.credentials.password = ''
    passwordRepeat.value = ''
    showPageContent();
  }

}

const pageContent = ref(null as null | HTMLElement);
const showPageContent = () => {
  (pageContent.value as HTMLElement).scrollIntoView({ behavior: "instant" });
};
</script>

<template>
  <form class="user-data" onsubmit="return false" ref="pageContent">
    <div class="user-data__set">
      <h2 class="page-title">Register</h2>
      <button
        class="user-data__button btn btn-warning"
        type="button"
        @click="$emit('login')"
      >
        Log-in
      </button>
    </div>
    <div class="user-data__item form-group">
      <label for="name">Name</label>
      <input
        class="form-control"
        id="name"
        placeholder="Enter your name"
        v-model="user.info.name"
      />
    </div>
    <div class="user-data__item form-group">
      <label>Who are you?</label>
      <div class="form-check user-data__radio">
        <div class="user-data__radio-option">
          <input
            class="form-check-input"
            type="radio"
            id="student"
            :value="Role.STUDENT"
            v-model="user.info.role"
          />
          <label for="student" class="form-check-label">Student</label>
        </div>
        <div class="user-data__radio-option">
          <input
            class="form-check-input"
            type="radio"
            id="teacher"
            :value="Role.TEACHER"
            v-model="user.info.role"
          />
          <label for="teacher" class="form-check-label">Teacher</label>
        </div>
      </div>
    </div>
    <div class="user-data__item form-group">
      <label for="username">Username</label>
      <input
        class="form-control"
        id="register-username"
        placeholder="Enter username"
        v-model="user.credentials.username"
      />
    </div>
    <div class="user-data__item form-group">
      <label for="register-password">Password</label>
      <input
        type="password"
        class="form-control"
        id="register-password"
        placeholder="Enter password"
        v-model="user.credentials.password"
      />
    </div>
    <div class="user-data__item form-group">
      <label for="password-repeat">Password</label>
      <input
        type="password"
        class="form-control"
        id="password-repeat"
        placeholder="Repeat password"
        v-model="passwordRepeat"
      />
    </div>
    <button @click="register()" type="submit" class="user-data__button btn btn-primary">
      Register
    </button>
  </form>
</template>

<style scoped lang="scss">
@import "@/assets/styles/login.scss";
</style>
