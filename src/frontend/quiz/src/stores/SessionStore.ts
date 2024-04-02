import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useRouter } from "vue-router";
import axios from 'axios';

import type { UserInfo } from '@/types/UserTypes.ts'
import { BASE_URL } from '@/constants/constants';


export const useSessionStore = defineStore(
  'session',
  () => {
    const userInfo = ref(null as null | UserInfo)
    const refreshTokenInterval = ref(undefined as undefined | ReturnType<typeof setInterval>);
    const refreshToken = async () => {
      if (userInfo.value === null) {
        return;
      }
      await axios.request({
        method: 'GET',
        url: BASE_URL + '/frontend_api/refresh_token',
        headers: { Authorization: "Bearer " + userInfo.value?.token },
        timeout: 10000
      }).then((response) => {
        userInfo.value = {
          username: userInfo.value?.username,
          name: userInfo.value?.name,
          role: userInfo.value?.role,
          token: response.data as string
        } as UserInfo;
        console.log('token refreshed on ' + (new Date()).toLocaleString())
      }).catch((err) => {
        // console.log('Error: ' + err.message)
        userInfo.value === null;
        const router = useRouter();
        router.push({ name: "login" });
      });
    }
    const setTokenRefresh = () => {
      clearInterval(refreshTokenInterval.value);
      refreshToken()
      refreshTokenInterval.value = setInterval(refreshToken, 5*60*1000);
    }
    const alertError = (error: string, reason: string) => {
      const alertElement = document.getElementById("alert") as HTMLElement;
      alertElement.innerHTML = `
        <p>
          <b>Error:</b>
          <br>${error}
        </p>
        <p>
          <b>Reason:</b>
          <br>${reason}
        </p>
      `
      alertElement.style.display = "block";
      setTimeout(() => {
        alertElement.scrollIntoView({ behavior: "smooth" });
      }, 10)
      setTimeout(() => {
        alertElement.style.display = "none";
      }, 5000);
    }
    return { userInfo, setTokenRefresh, alertError }
  },
  {
    persist: {
      storage: sessionStorage
    }
  }
)
