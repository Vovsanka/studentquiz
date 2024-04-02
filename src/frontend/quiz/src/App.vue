<script setup lang="ts">
import { ref, onBeforeMount } from "vue";
import { RouterLink, RouterView } from "vue-router";

import { useSessionStore } from "@/stores/SessionStore";
import { Role } from "./types/UserTypes";

const session = useSessionStore();

const pageContent = ref(null as null | HTMLElement);

onBeforeMount(() => {
  session.setTokenRefresh();
});

const showPageContent = () => {
  (pageContent.value as HTMLElement).scrollIntoView({ behavior: "smooth" });
};
</script>

<template>
  <header>
    <nav class="step navbar navbar-expand-lg bg-light">
      <ul class="nav-list navbar-nav me-auto mb-2 mb-lg-0">
        <li class="nav-list__item nav-item" @click="showPageContent">
          <RouterLink to="/" class="nav-link">Home</RouterLink>
        </li>
        <li
          class="nav-list__item nav-item"
          v-if="
            session.userInfo?.role == Role.TEACHER ||
            session.userInfo?.role == Role.STUDENT
          "
          @click="showPageContent"
        >
          <RouterLink to="/quiz" class="nav-link" id="quiz">Quiz</RouterLink>
        </li>
        <li
          class="nav-list__item nav-item"
          v-if="
            session.userInfo?.role == Role.TEACHER || session.userInfo?.role == Role.ADMIN
          "
          @click="showPageContent"
        >
          <RouterLink to="/test" class="nav-link">Test</RouterLink>
        </li>
        <li
          class="nav-list__item nav-item"
          v-if="
            session.userInfo?.role == Role.TEACHER || session.userInfo?.role == Role.ADMIN
          "
          @click="showPageContent"
        >
          <RouterLink to="/subject" class="nav-link">Subject</RouterLink>
        </li>
        <li class="nav-list__item nav-item" @click="showPageContent">
          <RouterLink to="/login" class="nav-link">Log in</RouterLink>
        </li>
      </ul>
    </nav>
  </header>

  <div class="step content" ref="pageContent">
    <div id="alert" class="alert alert-danger" role="alert" />
    <RouterView />
  </div>
</template>

<style scoped lang="scss">
nav {
  width: 100vw;
  z-index: 10;
  .nav-list {
    font-size: 2.5rem;
    width: 100%;
    display: flex;
    justify-content: space-around;

    &__item {
      margin: 5px 20px 5px 0;
      border: 5px solid #eeeeee;
      width: 100%;
      text-align: center;
    }
  }
}
</style>
