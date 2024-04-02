<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from "vue";
import axios from "axios";

import TestContainer from "@/components/tests/TestContainer.vue";

import { useSessionStore } from "@/stores/SessionStore";
import type { TestInstance, Test, CheckedAttempt, TestSummary } from "@/types/TestTypes";
import { ModeType } from "@/types/OtherTypes";
import type { UserInfo } from "@/types/UserTypes";
import { BASE_URL } from "@/constants/constants";
import { Role } from "@/types/UserTypes";

const session = useSessionStore();

const emit = defineEmits(["close"]);

const props = defineProps<{
  testInstance: null | TestInstance;
  subjectId: null | string;
}>();

const testMode = ref(null as null | ModeType);
const checkedAttempt = ref(null as null | CheckedAttempt);
const taskResults = ref(null as null | Array<Array<number>>);
const showStudentResults = ref(false as boolean);
const summary = ref({} as TestSummary);
const studentAttempts = ref([] as Array<CheckedAttempt>);
const studentAttemptsNames = ref([] as Array<string>);
const fetchResultsInterval = ref(undefined as undefined | ReturnType<typeof setInterval>);

onMounted(() => {
  if (props.testInstance?.solution_attempts.length === 1) {
    checkedAttempt.value = props.testInstance?.solution_attempts[0];
  }
});

onBeforeUnmount(() => {
  clearInterval(fetchResultsInterval.value);
});

const close = () => {
  emit("close", props.subjectId);
};

const startTest = () => {
  setTestMode(ModeType.RUN);
};

const finishTest = () => {
  testMode.value = null;
};

const fetchResults = async () => {
  await axios
    .request({
      method: "GET",
      url:
        BASE_URL +
        "/frontend_api/get_task_results/" +
        props.subjectId +
        "?test_id=" +
        props.testInstance?.test.info.id +
        "&remark=" +
        props.testInstance?.remark,
      headers: {
        Authorization: "Bearer " + session.userInfo?.token,
      },
      timeout: 10000,
    })
    .then((response) => {
      taskResults.value = response.data as Array<Array<number>>;
      console.log("fetched task results");
    })
    .catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log("Error: " + errorMessage[0] + " Reason: " + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1]);
    });
  await axios
    .request({
      method: "GET",
      url:
        BASE_URL +
        "/frontend_api/get_test_summary/" +
        props.subjectId +
        "?test_id=" +
        props.testInstance?.test.info.id +
        "&remark=" +
        props.testInstance?.remark,
      headers: {
        Authorization: "Bearer " + session.userInfo?.token,
      },
      timeout: 10000,
    })
    .then((response) => {
      summary.value = response.data as TestSummary;
      console.log("fetched test summary");
    })
    .catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log("Error: " + errorMessage[0] + " Reason: " + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1]);
    });
  await axios
    .request({
      method: "GET",
      url:
        BASE_URL +
        "/frontend_api/get_student_results/" +
        props.subjectId +
        "?test_id=" +
        props.testInstance?.test.info.id +
        "&remark=" +
        props.testInstance?.remark,
      headers: {
        Authorization: "Bearer " + session.userInfo?.token,
      },
      timeout: 10000,
    })
    .then((response) => {
      studentAttempts.value = (response.data as Array<string>).map((jsonStr) =>
        JSON.parse(jsonStr)
      ) as Array<CheckedAttempt>;
      console.log("fetched student results");
    })
    .catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log("Error: " + errorMessage[0] + " Reason: " + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1]);
    });
  studentAttemptsNames.value = [];
  for (const attempt of studentAttempts.value) {
    await axios
      .request({
        method: "GET",
        url:
          BASE_URL + "/frontend_api/get_user_info/" + attempt.solution_attempt.solved_by,
        headers: { Authorization: "Bearer " + session.userInfo?.token },
        timeout: 10000,
      })
      .then((response) => {
        studentAttemptsNames.value.push((response.data as UserInfo).name);
      })
      .catch((err) => {
        const errorMessage = err.response.data as Array<string>;
        console.log("Error: " + errorMessage[0] + " Reason: " + errorMessage[1]);
        session.alertError(errorMessage[0], errorMessage[1]);
      });
  }
  console.log("students info fetched");
};

const setTestMode = (newTestMode: ModeType) => {
  showStudentResults.value = false;
  testMode.value = null;
  clearInterval(fetchResultsInterval.value);
  setTimeout(() => {
    testMode.value = newTestMode;
    if (
      testMode.value == ModeType.RESULTS ||
      testMode.value == ModeType.ANSWERS_RESULTS
    ) {
      fetchResults();
      fetchResultsInterval.value = setInterval(fetchResults, 10000);
      showTestContent();
    }
  }, 5);
  setTimeout(showTestContent, 10);
};

const saveTestAttempt = async (answers: Array<any>) => {
  let formData = new FormData();
  formData.append("test_id", JSON.stringify(props.testInstance?.test.info.id as string));
  formData.append("remark", JSON.stringify(props.testInstance?.remark as string));
  formData.append("answers", JSON.stringify(answers));
  await axios
    .request({
      method: "POST",
      url: BASE_URL + "/frontend_api/save_test_attempt/" + props.subjectId,
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      data: formData,
      timeout: 10000,
    })
    .then((response) => {
      checkedAttempt.value = response.data as CheckedAttempt;
      testMode.value = null;
      console.log("Test attempt saved");
      setTestMode(ModeType.STUDENT_RESULTS);
    })
    .catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log("Error: " + errorMessage[0] + " Reason: " + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1]);
    });
};

const openStudentResults = async () => {
  testMode.value = null;
  clearInterval(fetchResultsInterval.value);
  fetchResults();
  fetchResultsInterval.value = setInterval(fetchResults, 10000);
  showStudentResults.value = false;
  setTimeout(() => {
    showStudentResults.value = true;
  }, 10);
};

const testContent = ref(null as null | HTMLElement);
const showTestContent = () => {
  if (testContent.value !== null) {
    (testContent.value as HTMLElement).scrollIntoView({ behavior: "smooth" });
  }
};
</script>

<template>
  <div class="test-instance">
    <h2>{{ props.testInstance?.test.info.name }}</h2>
    <table>
      <tbody>
        <tr>
          <td>Description:</td>
          <td>
            {{ props.testInstance?.test.info.description }}
          </td>
        </tr>
        <tr>
          <td>Publish remark:</td>
          <td>{{ props.testInstance?.remark }}</td>
        </tr>
        <tr v-if="session.userInfo?.role == Role.TEACHER">
          <td>Published by:</td>
          <td>{{ props.testInstance?.published_by }}</td>
        </tr>
        <tr v-if="session.userInfo?.role == Role.TEACHER">
          <td>Published at:</td>
          <td>
            {{ new Date(props.testInstance?.published_at as string).toLocaleString() }}
          </td>
        </tr>
        <tr>
          <td>Percents to pass:</td>
          <td>{{ props.testInstance?.test?.pass_percents }}%</td>
        </tr>
      </tbody>
    </table>
    <div class="control">
      <button class="btn btn-danger" @click="close()">Return</button>
      <button
        v-if="session.userInfo?.role == Role.STUDENT && checkedAttempt === null"
        class="btn btn-success"
        @click="startTest()"
      >
        {{ "Start test" }}
      </button>
      <button
        v-if="session.userInfo?.role == Role.STUDENT && checkedAttempt !== null"
        class="btn btn-primary"
        @click="setTestMode(ModeType.STUDENT_RESULTS)"
      >
        View results
      </button>
      <button
        v-if="session.userInfo?.role == Role.TEACHER"
        class="btn btn-warning"
        @click="setTestMode(ModeType.ANSWERS)"
      >
        {{ "Answers" }}
      </button>
      <button
        v-if="session.userInfo?.role == Role.TEACHER"
        class="btn btn-primary"
        @click="setTestMode(ModeType.RESULTS)"
      >
        {{ "Results" }}
      </button>
      <button
        v-if="session.userInfo?.role == Role.TEACHER"
        class="btn btn-success"
        @click="setTestMode(ModeType.ANSWERS_RESULTS)"
      >
        {{ "Answers + Results" }}
      </button>
      <button
        v-if="session.userInfo?.role == Role.TEACHER"
        class="btn btn-info"
        @click="openStudentResults()"
      >
        Student results
      </button>
    </div>
    <div v-if="testMode !== null" ref="testContent">
      <div
        v-if="testMode == ModeType.RESULTS || testMode == ModeType.ANSWERS_RESULTS"
        class="test-instance__summary"
      >
        <h3>Passed: {{ summary.passed }}/{{ summary.attempts_count }}</h3>
        <h3>Average score: {{ Math.round(summary.average ?? 0) }}%</h3>
      </div>
      <TestContainer
        @close="finishTest"
        @publish="() => {}"
        @test-attempt="saveTestAttempt"
        :testId="null"
        :test="(props.testInstance?.test as Test)"
        :checkedAttempt="checkedAttempt"
        :mode="testMode"
        :taskResults="taskResults"
      />
    </div>
    <div v-if="showStudentResults" class="test-instance__students">
      <h3 style="font-weight: bold">Students:</h3>
      <table>
        <thead>
          <tr>
            <th style="font-weight: bold">Name</th>
            <th style="font-weight: bold">Username</th>
            <th style="font-weight: bold">Score</th>
            <th style="font-weight: bold">Passed</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(attempt, index) in studentAttempts" :key="index">
            <td>
              <span> {{ studentAttemptsNames[index] }}</span>
            </td>
            <td>
              <span>
                {{ attempt.solution_attempt.solved_by }}
              </span>
            </td>
            <td>
              <span> {{ attempt.attempt_percents.toFixed(1) }}% </span>
            </td>
            <td>
              <span>
                {{ attempt.passed ? "YES" : "NO" }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped lang="scss">
.test-instance {
  min-width: 350px;
  font-size: 1rem;
  border: 3px solid orangered;

  & h2 {
    margin: 10px;
    font-size: 2.5rem;
  }

  & table {
    border-collapse: separate;
    border-spacing: 10px 10px;

    & td {
      vertical-align: top;
    }

    & td:first-child {
      font-style: italic;
      width: 120px;
    }

    & td:nth-child(2) {
      overflow-wrap: break-word;
      word-wrap: break-word;
      word-break: break-word;
    }
  }

  & h3 {
    font-size: 1.5rem;
  }

  &__summary {
    margin-left: 10px;
  }

  &__students {
    & table {
      border-collapse: separate;
      border-spacing: 10px 10px;

      & td:first-child {
        font-style: normal;
      }

      & td {
        vertical-align: top;
        overflow-wrap: break-word;
        word-wrap: break-word;
        word-break: break-word;
      }
    }

    & h3 {
      margin-left: 10px;
    }
  }
}

.control {
  padding: 25px 0;
  width: 100%;
  background: white;
  display: block;

  & button {
    font-size: 1rem;
    width: 200px;
    margin: 10px;
  }
}
</style>
