<script setup lang="ts">
import { ref, onBeforeMount } from "vue";
import { useRouter } from "vue-router";

import TestList from "@/components/tests/TestList.vue";
import TestContainer from "@/components/tests/TestContainer.vue";
import TestPublisher from "@/components/tests/TestPublisher.vue";

import { useSessionStore } from "@/stores/SessionStore";
import { ModeType } from "@/types/OtherTypes";

const session = useSessionStore();
const testContainer = ref(false as boolean);
const testPublisher = ref(false as boolean);

const testIdTemp = ref(null as null | string);
const testContainerMode = ref(ModeType.EDIT);

onBeforeMount(() => {
  if (session.userInfo === null) {
    const router = useRouter();
    router.push({ name: "login" });
  }
});

const openTestContainer = (testId: null | string = null, mode = ModeType.EDIT) => {
  closeAll();
  testIdTemp.value = testId;
  testContainerMode.value = mode;
  testContainer.value = true;
};

const openTestPublisher = (testId: null | string = null) => {
  closeAll();
  testIdTemp.value = testId;
  testPublisher.value = true;
};

const closeAll = () => {
  closeTestContainer();
  closeTestPublisher();
};

const closeTestContainer = () => {
  testContainer.value = false;
};

const closeTestPublisher = () => {
  testPublisher.value = false;
};
</script>

<template>
  <div class="page-content">
    <TestList
      @testContainer="openTestContainer"
      @testPublisher="openTestPublisher"
      v-if="!testContainer && !testPublisher"
    />
    <TestContainer
      @close="closeTestContainer"
      @publish="openTestPublisher"
      :testId="testIdTemp"
      :test="null"
      :checkedAttempt="null"
      :taskResults="null"
      :mode="testContainerMode"
      v-if="testContainer"
      ref="TestContainerComponent"
    />
    <TestPublisher
      @close="closeTestPublisher"
      :testId="testIdTemp"
      :subjectId="null"
      v-if="testPublisher"
      ref="TestPublisherComponent"
    />
  </div>
</template>

<style scoped lang="scss"></style>
