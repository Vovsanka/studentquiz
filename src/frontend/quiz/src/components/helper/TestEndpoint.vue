<script setup lang="ts">
import axios from "axios";
import { useSessionStore } from "@/stores/SessionStore";
import { BASE_URL } from "@/constants/constants";

const props = defineProps({
  relativePath: String,
});

// remove this test endpoint code then!!!
const session = useSessionStore();

const checkEndpoint = async () => {
  console.log(session.userInfo?.token);
  await axios
    .request({
      method: "GET",
      url: BASE_URL + "/" + props.relativePath,
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      timeout: 2000,
    })
    .then((response) => {
      console.log(response);
      console.log(response.data);
    })
    .catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log("Error: " + errorMessage[0] + " Reason: " + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1]);
    });
};
</script>

<template>
  <button @click="checkEndpoint()" class="btn btn-danger">Endpoint!</button>
</template>

<style scoped lang="scss"></style>
