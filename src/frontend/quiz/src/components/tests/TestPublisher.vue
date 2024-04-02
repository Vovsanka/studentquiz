<script setup lang="ts">
import { ref, onMounted } from "vue";
import axios from "axios";

import { useSessionStore } from "@/stores/SessionStore";
import type { TestInfo } from "@/types/TestTypes";
import type { SubjectInfo } from "@/types/SubjectTypes";
import { BASE_URL } from "@/constants/constants";

const props = defineProps<{
  testId: string | null;
  subjectId: string | null;
}>();

const emit = defineEmits(["close"]);

const session = useSessionStore();

const testInfo = ref({
  id: "",
  name: "",
  description: "",
} as TestInfo);
const subjectInfo = ref({
  id: "",
  name: "",
  description: "",
} as SubjectInfo);
const myTests = ref([] as Array<TestInfo>);
const mySubjects = ref([] as Array<SubjectInfo>);
const remark = ref("" as string);

onMounted(async () => {
  await fetchMySubjects();
  await fetchMyTests();
  if (props.subjectId !== null) {
    await fetchSubjectInfo(props.subjectId);
  }
  if (props.testId !== null) {
    await fetchTestInfo(props.testId);
  }
});

const fetchTestInfo = async (testId: string) => {
  await axios
    .request({
      method: "GET",
      url: BASE_URL + "/frontend_api/get_test_info/" + testId,
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      timeout: 10000,
    })
    .then((response) => {
      testInfo.value = response.data as TestInfo;
      console.log("fetched test info");
    })
    .catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log("Error: " + errorMessage[0] + " Reason: " + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1]);
    });
};

const fetchSubjectInfo = async (subjectId: string) => {
  await axios
    .request({
      method: "GET",
      url: BASE_URL + "/frontend_api/get_subject_info/" + subjectId,
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      timeout: 10000,
    })
    .then((response) => {
      subjectInfo.value = response.data as SubjectInfo;
      console.log("fetched subject info");
    })
    .catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log("Error: " + errorMessage[0] + " Reason: " + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1]);
    });
};

const fetchMySubjects = async () => {
  await axios
    .request({
      method: "GET",
      url: BASE_URL + "/frontend_api/get_my_subjects_info",
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      timeout: 10000,
    })
    .then((response) => {
      mySubjects.value = (response.data as Array<string>).map((jsonStr) =>
        JSON.parse(jsonStr)
      ) as Array<SubjectInfo>;
      console.log("fetched my subjects info");
    })
    .catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log("Error: " + errorMessage[0] + " Reason: " + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1]);
    });
};

const fetchMyTests = async () => {
  await axios
    .request({
      method: "GET",
      url: BASE_URL + "/frontend_api/get_my_tests_info",
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      timeout: 10000,
    })
    .then((response) => {
      myTests.value = (response.data as Array<string>).map((jsonStr) =>
        JSON.parse(jsonStr)
      ) as Array<TestInfo>;
      console.log("fetched my tests info");
    })
    .catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log("Error: " + errorMessage[0] + " Reason: " + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1]);
    });
};

const publishTest = async () => {
  if (testInfo.value.id === "" || subjectInfo.value.id === "") {
    alert("Error: choose subject and test to publish");
    return;
  }
  let formData = new FormData();
  formData.append("remark", JSON.stringify(remark.value));
  await axios
    .request({
      method: "POST",
      url:
        BASE_URL +
        `/frontend_api/publish_test/${subjectInfo.value.id}/${testInfo.value.id}`,
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      data: formData,
      timeout: 10000,
    })
    .then((response) => {
      console.log("the test has been published on the subject");
      emit("close", subjectInfo.value.id);
    })
    .catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log("Error: " + errorMessage[0] + " Reason: " + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1]);
    });
  emit("close");
};

const cancelPublish = async () => {
  emit("close");
};
</script>

<template>
  <div class="publisher">
    <h1 class="page-title">Test Publisher</h1>
    <table class="table publisher__body-table">
      <tbody>
        <tr>
          <td><label for="subject-selector">Publish to subject:</label></td>
          <td>
            <div>
              <select
                v-model="subjectInfo"
                id="subject-selector"
                class="publisher__subject-selector form-select"
              >
                <option v-for="(info, index) in mySubjects" :value="info">
                  {{ info.name }}
                </option>
              </select>
            </div>
          </td>
        </tr>
        <tr>
          <td>Subject name:</td>
          <td>{{ subjectInfo.name }}</td>
        </tr>
        <tr>
          <td>Subject description:</td>
          <td class="publisher__description">{{ subjectInfo.description }}</td>
        </tr>
      </tbody>
    </table>
    <table class="table publisher__body-table">
      <tbody>
        <tr>
          <td><label for="test-selector">Publish test:</label></td>
          <td>
            <div>
              <select
                v-model="testInfo"
                id="test-selector"
                class="publisher__subject-selector form-select"
              >
                <option v-for="(info, index) in myTests" :value="info">
                  {{ info.name }}
                </option>
              </select>
            </div>
          </td>
        </tr>
        <tr>
          <td>Test name:</td>
          <td>{{ testInfo.name }}</td>
        </tr>
        <tr>
          <td>Test description:</td>
          <td class="publisher__description">{{ testInfo.description }}</td>
        </tr>
      </tbody>
    </table>
    <table class="table publisher__body-table">
      <tbody>
        <tr class="publisher__remark">
          <td><label for="remark-input">Remark: (1word): </label></td>
          <td>
            <input
              id="remark-input"
              class="form-control"
              v-model="remark"
              placeholder="identify same tests"
            />
          </td>
        </tr>
      </tbody>
    </table>
    <div class="publisher__buttons">
      <button @click="cancelPublish()" class="btn btn-danger">Cancel</button>
      <button @click="publishTest()" class="btn btn-success">Publish</button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.publisher {
  margin: 30px 0;

  & table {
    margin: 50px 0;

    & td:first-child {
      font-style: italic;
      width: 150px;
    }

    & td:nth-child(2) {
      overflow-wrap: break-word;
      word-wrap: break-word;
      word-break: break-word;
    }
  }

  &__description {
    vertical-align: middle;
    font-size: 1rem;
  }

  &__body-table {
    width: auto;
    font-size: 1.5rem;
  }

  & select,
  & input {
    width: 200px;
  }

  &__buttons {
    & button {
      width: 200px;
      margin: 10px 20px 0 0;
    }
  }
}
</style>
