<script setup lang="ts">
import { ref, onBeforeMount } from "vue";
import { useRouter } from "vue-router";

import SubjectList from "@/components/subjects/SubjectList.vue";
import SubjectContainer from "@/components/subjects/SubjectContainer.vue";
import TestInstanceContainer from "@/components/tests/TestInstanceContainer.vue";
import { ModeType } from "@/types/OtherTypes";
import type { TestInstance } from "@/types/TestTypes";

import { useSessionStore } from "@/stores/SessionStore";

const session = useSessionStore();

onBeforeMount(() => {
  if (session.userInfo === null) {
    const router = useRouter();
    router.push({ name: "login" });
  }
});

const subjectContainer = ref(false as boolean);
const testInstance = ref(false as boolean);

const subjectIdTemp = ref(null as null | string);
const testInstanceTemp = ref(null as null | TestInstance);
const subjectContainerMode = ref(ModeType.VIEW as ModeType);

const openSubjectContainer = (subjectId: null | string = null, mode = ModeType.RUN) => {
  closeAll();
  subjectIdTemp.value = subjectId;
  subjectContainerMode.value = mode;
  subjectContainer.value = true;
};

const openTestInstance = (subjectId: null | string, testInstanceObject: TestInstance) => {
  closeAll();
  subjectIdTemp.value = subjectId;
  testInstanceTemp.value = testInstanceObject;
  testInstance.value = true;
};

const closeAll = () => {
  closeSubjectContainer();
  closeTestInstance();
};

const closeSubjectContainer = () => {
  subjectContainer.value = false;
  subjectIdTemp.value = null;
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
      :mode="ModeType.RUN"
      v-if="!subjectContainer && !testInstance"
    />
    <SubjectContainer
      @close="closeSubjectContainer"
      @publish="() => {}"
      @testinstance="openTestInstance"
      :subjectId="subjectIdTemp"
      :mode="subjectContainerMode"
      v-if="subjectContainer"
      ref="SubjectContainerComponent"
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
