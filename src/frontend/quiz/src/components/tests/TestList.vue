<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import axios from "axios";
import { useWindowSize } from "@vueuse/core";

import { useSessionStore } from "@/stores/SessionStore";
import { BASE_URL } from "@/constants/constants";
import type { Test, TestInfo } from "@/types/TestTypes";
import type { SubjectInfo } from "@/types/SubjectTypes";
import { ModeType } from "@/types/OtherTypes";
import { Role } from "@/types/UserTypes";

const emit = defineEmits(["testContainer", "testPublisher"]);

const windowWidth = useWindowSize().width;

const session = useSessionStore();

const tests = ref([] as Array<TestInfo>);
const publishedTable = reactive({} as { [key: string]: string[] });
const testAuthors = ref([] as Array<string>);

onMounted(async () => {
  await fetchMyTests();
  await buildPublishedTable();
});

const buildPublishedTable = async () => {
  if (session.userInfo?.role === Role.TEACHER) {
    for (const test of tests.value) {
      const subjects = (await fetchSubjectsPublishedOn(test.id)) as Array<SubjectInfo>; // must be empty!
      publishedTable[test.id] = subjects.map((subjectInfo) => subjectInfo.name);
    }
  }
};

const fetchMyTests = async () => {
  if (session.userInfo?.role === Role.TEACHER) {
    await axios
      .request({
        method: "GET",
        url: BASE_URL + "/frontend_api/get_my_tests_info",
        headers: { Authorization: "Bearer " + session.userInfo?.token },
        timeout: 10000,
      })
      .then((response) => {
        tests.value = (response.data as Array<string>).map((jsonStr) =>
          JSON.parse(jsonStr)
        ) as Array<TestInfo>;
        console.log("fetched my tests");
      })
      .catch((err) => {
        const errorMessage = err.response.data as Array<string>;
        console.log("Error: " + errorMessage[0] + " Reason: " + errorMessage[1]);
        session.alertError(errorMessage[0], errorMessage[1]);
      });
  } else if (session.userInfo?.role === Role.ADMIN) {
    await axios
      .request({
        method: "GET",
        url: BASE_URL + "/frontend_api/get_all_tests_info",
        headers: { Authorization: "Bearer " + session.userInfo?.token },
        timeout: 10000,
      })
      .then((response) => {
        tests.value = (response.data["tests_info"] as Array<string>).map((jsonStr) =>
          JSON.parse(jsonStr)
        ) as Array<TestInfo>;
        testAuthors.value = response.data["tests_teachers"] as Array<string>;
        console.log("fetched all tests");
      })
      .catch((err) => {
        const errorMessage = err.response.data as Array<string>;
        console.log("Error: " + errorMessage[0] + " Reason: " + errorMessage[1]);
        session.alertError(errorMessage[0], errorMessage[1]);
      });
  }
};

const fetchSubjectsPublishedOn = async (testId: string) => {
  let result = [] as Array<SubjectInfo>;
  await axios
    .request({
      method: "GET",
      url: BASE_URL + "/frontend_api/get_subjects_info_published/" + testId,
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      timeout: 10000,
    })
    .then((response) => {
      result = (response.data as Array<string>).map((jsonStr) =>
        JSON.parse(jsonStr)
      ) as Array<SubjectInfo>;
      console.log("fetched subjects the tests are published on");
    })
    .catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log("Error: " + errorMessage[0] + " Reason: " + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1]);
    });
  return result;
};

const viewTest = (testId: string) => {
  emit("testContainer", testId, ModeType.VIEW);
};

const createTest = () => {
  emit("testContainer");
};

const publishTest = async (testId: string) => {
  emit("testPublisher", testId);
};

const deleteTest = async (testId: string) => {
  await axios
    .request({
      method: "DELETE",
      url: BASE_URL + "/frontend_api/delete_test/" + testId,
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      timeout: 10000,
    })
    .then((response) => {
      console.log("test deleted");
    })
    .catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log("Error: " + errorMessage[0] + " Reason: " + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1]);
    });
  // reload the table
  await fetchMyTests();
};

const bigWindow = computed(() => {
  return windowWidth.value >= 1280;
});

const smallWindow = computed(() => {
  return windowWidth.value < 640;
});
</script>

<template>
  <section class="my-tests">
    <h1 class="page-title">Manage my tests</h1>
    <table class="table">
      <thead>
        <tr>
          <th scope="col" v-if="!smallWindow">#</th>
          <th scope="col">Name</th>
          <th scope="col" v-if="bigWindow">Description</th>
          <th scope="col" v-if="!smallWindow && session.userInfo?.role === Role.TEACHER">
            Published on
          </th>
          <th scope="col" v-if="session.userInfo?.role === Role.ADMIN">Author</th>
          <th scope="col"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(test, index) in tests" :key="index">
          <th scope="row" v-if="!smallWindow">{{ index + 1 }}</th>
          <td class="my-tests__test-name">
            {{ test.name }}
          </td>
          <td class="my-tests__test-description" v-if="bigWindow">
            {{ test.description }}
          </td>
          <td
            class="my-tests__test-subjects"
            v-if="!smallWindow && session.userInfo?.role === Role.TEACHER"
          >
            <p v-for="(subject, index) in publishedTable[test.id]" :key="index">
              {{ subject }}
            </p>
          </td>
          <td v-if="session.userInfo?.role === Role.ADMIN">
            {{ testAuthors[index] }}
          </td>
          <td :style="bigWindow ? 'width: auto' : 'width: 160px'">
            <div class="my-tests__test-buttons">
              <button
                @click="deleteTest(test.id)"
                class="my-tests__operation-button btn btn-danger"
              >
                Delete
              </button>
              <button
                v-if="session.userInfo?.role === Role.TEACHER"
                @click="viewTest(test.id)"
                class="my-tests__operation-button btn btn-info"
              >
                View
              </button>
              <button
                v-if="session.userInfo?.role === Role.TEACHER"
                @click="publishTest(test.id)"
                class="my-tests__operation-button btn btn-success"
              >
                Publish
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    <button
      v-if="session.userInfo?.role === Role.TEACHER"
      @click="createTest()"
      class="my-tests__create-button btn btn-primary"
    >
      Create Test
    </button>
  </section>
</template>

<style scoped lang="scss">
.my-tests {
  margin: 30px 5px;
  max-width: 90vw;

  & table {
    border-collapse: separate;
    border-spacing: 0 10px;
    display: table;
  }

  & th {
    font-size: 1.5rem;
  }

  & td {
    overflow-wrap: break-word;
    word-wrap: break-word;
    word-break: break-word;

    vertical-align: center;
  }

  &__test-name {
    font-size: 1.5rem;
  }

  &__test-description {
    overflow-wrap: break-word;
    word-wrap: break-word;
    word-break: break-word;
  }

  &__test-subjects {
    overflow: auto;

    & p {
      margin-bottom: 20px;
    }
  }

  &__create-button {
    font-size: 2rem;
    width: 250px;
  }

  &__test-buttons {
    display: block;
  }

  &__operation-button {
    font-size: 1.5rem;
    min-width: 120px;
    height: 100%;
    padding: 10px;
    margin: 10px;
  }
}
</style>
