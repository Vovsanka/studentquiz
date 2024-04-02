<script setup lang="ts">
import { ref, onBeforeMount } from "vue";
import { useRouter } from "vue-router";

import SubjectList from "@/components/subjects/SubjectList.vue";
import SubjectContainer from "@/components/subjects/SubjectContainer.vue";
import TestPublisher from "@/components/tests/TestPublisher.vue";
import TestInstanceContainer from "@/components/tests/TestInstanceContainer.vue";
import { ModeType } from "@/types/OtherTypes";
import type { TestInstance } from "@/types/TestTypes";

import { useSessionStore } from "@/stores/SessionStore";

const session = useSessionStore();

const subjectContainer = ref(false as boolean);
const testPublisher = ref(false as boolean);
const testInstance = ref(false as boolean);

const subjectIdTemp = ref(null as null | string);
const testInstanceTemp = ref(null as null | TestInstance);
const subjectContainerMode = ref(ModeType.VIEW as ModeType);

onBeforeMount(() => {
  if (session.userInfo === null) {
    const router = useRouter();
    router.push({ name: "login" });
  }
});

const openSubjectContainer = (subjectId: null | string = null, mode = ModeType.VIEW) => {
  closeAll();
  subjectIdTemp.value = subjectId;
  subjectContainerMode.value = mode;
  subjectContainer.value = true;
};

const openTestPublisher = (subjectId: null | string = null) => {
  closeAll();
  subjectIdTemp.value = subjectId;
  testPublisher.value = true;
};

const openTestInstance = (subjectId: null | string, testInstanceObject: TestInstance) => {
  closeAll();
  subjectIdTemp.value = subjectId;
  testInstanceTemp.value = testInstanceObject;
  testInstance.value = true;
};

const closeAll = () => {
  closeSubjectContainer();
  closeTestPublisher();
  closeTestInstance();
};

const closeSubjectContainer = () => {
  subjectContainer.value = false;
  subjectIdTemp.value = null;
};

const closeTestPublisher = (subjectId: string | null = null) => {
  testPublisher.value = false;
  if (subjectId) {
    openSubjectContainer(subjectId);
  }
};

const closeTestInstance = (subjectId: string | null = null) => {
  testInstance.value = false;
  testInstanceTemp.value = null;
  if (subjectId) {
    openSubjectContainer(subjectId);
  }
};
</script>

<template>
  <div class="page-content">
    <SubjectList
      @subjectContainer="openSubjectContainer"
      :mode="ModeType.VIEW"
      v-if="!subjectContainer && !testPublisher && !testInstance"
    />
    <SubjectContainer
      @close="closeSubjectContainer"
      @publish="openTestPublisher"
      @testinstance="openTestInstance"
      :subjectId="subjectIdTemp"
      :mode="subjectContainerMode"
      v-if="subjectContainer"
      ref="SubjectContainerComponent"
    />
    <TestPublisher
      @close="closeTestPublisher"
      :testId="null"
      :subjectId="subjectIdTemp"
      v-if="testPublisher"
      ref="TestPublisherComponenft"
    />
    <TestInstanceContainer
      @close="closeTestInstance"
      :subjectId="subjectIdTemp"
      :testInstance="testInstanceTemp"
      v-if="testInstance"
      ref="TestInstanceComponent"
    />
  </div>
</template>

<style scoped lang="scss"></style>
