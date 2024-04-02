<script setup lang="ts">
import { ref, onMounted } from "vue";
import axios from "axios";

import Login from "./Login.vue";
import Register from "./Register.vue";
import { BASE_URL } from "@/constants/constants";
import { Role, type Credentials, type UserInfo, type User } from "@/types/UserTypes";
import { useSessionStore } from "@/stores/SessionStore";

const session = useSessionStore();

const LoginComponent = ref();

const registerMode = ref(false);

const allUsers = ref([] as Array<UserInfo>)

onMounted(async () => {
  if (session.userInfo?.role === Role.ADMIN) {
    await fetchAllUsers()
  }
})

const fetchAllUsers = async () => {
  await axios.request({
      method: "GET",
      url: BASE_URL + "/frontend_api/get_all_users_info",
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      timeout: 10000,
    })
    .then((response) => {
      allUsers.value = (response.data as Array<string>).map((jsonStr) =>
          JSON.parse(jsonStr)
        ) as Array<UserInfo>;
      console.log(allUsers.value)
    })
    .catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log('Error: ' + errorMessage[0] + ' Reason: ' + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1])
    });
};

const setRegisterMode = () => {
  registerMode.value = true;
};

const setLoginMode = async (credentials: null | Credentials = null) => {
  registerMode.value = false;
  if (credentials !== null) {
    await LoginComponent.value.login(credentials);
  }
  if (session.userInfo?.role === Role.ADMIN) {
    await fetchAllUsers()
  }
};

const deleteUser = async (username : string) => {
  await axios
    .request({
      method: "DELETE",
      url: BASE_URL + "/frontend_api/delete_user/" + username,
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      timeout: 10000,
    })
    .then((response) => {
      console.log("user deleted");
    })
    .catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log('Error: ' + errorMessage[0] + ' Reason: ' + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1])
    });
  await fetchAllUsers();
};
</script>

<template>
  <Register @login="setLoginMode" v-show="registerMode" />
  <Login
    @register="setRegisterMode"
    @login="setLoginMode"
    v-show="!registerMode"
    ref="LoginComponent"
  />
  <div v-if="session.userInfo?.role == Role.ADMIN">
    <h3 style="font-weight: bold">Users:</h3>
    <table>
      <thead>
        <tr>
          <th style="font-weight: bold">Name</th>
          <th style="font-weight: bold">Role</th>
          <th style="font-weight: bold">Username</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(user, index) in allUsers" :key="index">
          <td>
            {{ user.name }}
          </td>
          <td>
            {{ user.role }}
          </td>
          <td>
            <div class="username">
              {{ user.username }}
              <button class="btn btn-danger" @click="deleteUser(user.username)">X</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped lang="scss">
table {
  min-width: 350px;
  border-collapse: separate;
  border-spacing: 10px 10px;
  margin-bottom: 10px;

  & td {
    vertical-align: center;
    text-align: left;
    max-width: 700px;
    overflow-wrap: break-word;
    word-wrap: break-word;
    word-break: break-word;
  }

  & h3 {
    font-size: 1.5rem;
  }
}

.username {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 5px 0;

  & button {
    margin: 5px;
  }
}
</style>
