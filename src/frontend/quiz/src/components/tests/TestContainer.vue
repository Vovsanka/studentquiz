<script setup lang="ts">
import { ref, reactive, onMounted, toRaw, nextTick } from "vue";
import axios from "axios";

import SingleChoiceTask from "../tasks/SingleChoiceTask.vue";
import MultipleChoiceTask from "../tasks/MultipleChoiceTask.vue";
import { ModeType } from "@/types/OtherTypes";

import { useSessionStore } from "@/stores/SessionStore";
import type {
  Test,
  TestInfo,
  Task,
  SingleChoice,
  MultipleChoice,
  CheckedAttempt,
} from "@/types/TestTypes";
import { TaskType } from "@/types/TestTypes";
import { BASE_URL } from "@/constants/constants";

const session = useSessionStore();

const props = defineProps<{
  testId: null | string;
  test: null | Test;
  checkedAttempt: null | CheckedAttempt;
  taskResults: null | Array<Array<number>>;
  mode: ModeType;
}>();

const emit = defineEmits(["close", "publish", "test-attempt"]);
const mode = ref(props.mode as ModeType);
const saveTrigger = ref(false as boolean);

let taskUpdatesPending = 0 as number;

const test = reactive({
  info: {
    name: "",
    description: "",
    id: "",
  } as TestInfo,
  tasks: [] as Array<Task>,
  pass_percents: 0 as number,
} as Test);

onMounted(async () => {
  if (props.test !== null) initTest(props.test as Test);
  else await fetchTest(props.testId);
});

function initTest(tempTest: Test) {
  test.info = tempTest.info;
  test.tasks = tempTest.tasks;
  test.pass_percents = tempTest.pass_percents;
}

const fetchTest = async (testId: null | string) => {
  await axios
    .request({
      method: "GET",
      url: BASE_URL + "/frontend_api/get_test" + (testId !== null ? "/" + testId : ""),
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      timeout: 10000,
    })
    .then((response) => {
      initTest(response.data as Test);
      console.log("test fetched");
    })
    .catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log("Error: " + errorMessage[0] + " Reason: " + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1]);
    });
};

// editor buttons

const removeTask = async (taskIndex: number) => {
  await retrieveUpdates();
  const tempTasks = test.tasks;
  test.tasks = [];
  tempTasks.splice(taskIndex, 1);
  nextTick(() => {
    test.tasks = tempTasks;
    console.log(toRaw(test).tasks);
  });
};

const insertSingleChoiceTask = async (taskIndex: number = -1) => {
  await retrieveUpdates();
  let newTask = {
    question: "",
    tag: "",
    options: ["", "", ""],
    answer: 0,
    type: TaskType.SINGLE_CHOICE,
    points: 10,
  } as SingleChoice;
  // insert the new task
  if (taskIndex == -1) {
    test.tasks.push(newTask);
  } else {
    const tempTasks = [
      ...test.tasks.slice(0, taskIndex),
      newTask,
      ...test.tasks.slice(taskIndex),
    ];
    test.tasks = [];
    nextTick(() => {
      test.tasks = tempTasks;
    });
  }
};

const insertMultipleChoiceTask = async (taskIndex: number = -1) => {
  await retrieveUpdates();
  let newTask = {
    question: "",
    tag: "",
    options: ["", "", ""],
    answer: [],
    type: TaskType.MULTIPLE_CHOICE,
    points: 10,
  } as MultipleChoice;
  // insert the new task
  if (taskIndex == -1) {
    test.tasks.push(newTask);
  } else {
    const tempTasks = [
      ...test.tasks.slice(0, taskIndex),
      newTask,
      ...test.tasks.slice(taskIndex),
    ];
    test.tasks = [];
    nextTick(() => {
      test.tasks = tempTasks;
    });
  }
};

// control buttons

const close = () => {
  emit("close");
};

const setMode = (modeValue: ModeType) => {
  mode.value = modeValue;
};

const retrieveUpdates = async () => {
  // get all task modifications from the task child components
  await new Promise(function (resolve, reject) {
    taskUpdatesPending = test.tasks.length;
    saveTrigger.value = true;
    setInterval(() => {
      if (taskUpdatesPending == 0) {
        resolve("All test changes have been retrieved");
      }
    }, 5);
  })
    .finally(() => {
      saveTrigger.value = false;
    })
    .then((message) => {
      console.log(message);
    });
};

const saveTest = async () => {
  await retrieveUpdates();
  // make a post request with the whole test
  const testId = test.info.id;
  let formData = new FormData();
  formData.append("test", JSON.stringify(toRaw(test)));
  await axios
    .request({
      method: "PUT",
      url: BASE_URL + "/frontend_api/save_test/" + testId,
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      data: formData,
      timeout: 10000,
    })
    .then((response) => {
      console.log("test saved");
    })
    .catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log("Error: " + errorMessage[0] + " Reason: " + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1]);
    });
};

const submitTest = async () => {
  await retrieveUpdates();
  // make a post request only with the task answers
  emit(
    "test-attempt",
    toRaw(test).tasks.map((task) => task.answer)
  );
};

const updateTask = (taskIndex: number, task: Task) => {
  test.tasks[taskIndex] = task;
  taskUpdatesPending--;
};

const publishTest = async () => {
  await saveTest();
  emit("publish", test.info.id);
};

const getSingleChoiceAnswer = (index: number) => {
  return (props.checkedAttempt?.solution_attempt.answers[index] ?? null) as null | number;
};

const getMultipleChoiceAnswer = (index: number) => {
  return (props.checkedAttempt?.solution_attempt.answers[index] ??
    null) as null | Array<number>;
};

const getTaskPoints = (index: number) => {
  return (props.checkedAttempt?.task_points[index] ?? null) as null | number;
};

const getTaskResults = (index: number) => {
  if (props.taskResults === null) return null;
  return props.taskResults[index] as Array<number>;
};
</script>

<template>
  <div class="control" v-if="mode == ModeType.EDIT || mode == ModeType.VIEW">
    <button class="btn btn-danger" @click="close()">Return (cancel)</button>
    <button
      v-if="mode == ModeType.VIEW"
      class="btn btn-warning"
      @click="setMode(ModeType.EDIT)"
    >
      Edit
    </button>
    <button
      v-if="mode == ModeType.EDIT"
      class="btn btn-info"
      @click="setMode(ModeType.VIEW)"
    >
      View
    </button>
    <button
      class="btn btn-primary"
      @click="
        async () => {
          await saveTest();
          close();
        }
      "
    >
      Save edit
    </button>
    <button class="btn btn-success" @click="publishTest()">
      {{ "Save & Publish" }}
    </button>
  </div>
  <div v-if="mode == ModeType.STUDENT_RESULTS" class="student-results">
    <h2>
      <span>Test </span>
      <span v-if="checkedAttempt?.passed" class="student-results__passed">Passed: </span>
      <span v-else class="student-results__failed">Failed: </span>
      <span>
        {{ (checkedAttempt?.attempt_points as number).toFixed(1) }} /
        {{ checkedAttempt?.overall_points }} ({{
          (checkedAttempt?.attempt_percents as number).toFixed(1)
        }}
        %)
      </span>
    </h2>
  </div>
  <div class="editor">
    <div>
      <h2 v-if="mode == ModeType.VIEW">{{ test?.info?.name }}</h2>
      <div v-if="mode == ModeType.EDIT" class="editor__field">
        <label for="test-name">Test name: </label>
        <input
          v-model="test.info.name"
          class="form-control"
          id="test-name"
          placeholder="enter a test name"
        />
      </div>
    </div>
    <div>
      <h3 v-if="mode == ModeType.VIEW">
        <i>Description:</i> {{ test?.info?.description }}
      </h3>
      <div v-if="mode == ModeType.EDIT" class="editor__field">
        <label for="test-description">Test description: </label>
        <textarea
          v-model="test.info.description"
          class="form-control"
          id="test-description"
          type="text"
          placeholder="enter a test description"
        />
      </div>
    </div>
    <div>
      <h3 v-if="mode == ModeType.VIEW">
        <i>Percents to pass:</i> {{ (test?.pass_percents as number).toFixed(1) }}%
      </h3>
      <div v-if="mode == ModeType.EDIT" class="editor__field">
        <label for="test-percents">Percents to pass (%): </label>
        <input
          v-model="test.pass_percents"
          class="form-control"
          type="number"
          min="0"
          max="100"
          id="test-percents"
        />
      </div>
    </div>
    <div v-for="(task, index) in test?.tasks" :key="index" class="editor__task">
      <div v-if="mode == ModeType.EDIT" class="editor__task-insert">
        <button class="btn btn-success" @click="insertSingleChoiceTask(index)">
          + single-choice
        </button>
        <button class="btn btn-success" @click="insertMultipleChoiceTask(index)">
          + multiple-choice
        </button>
      </div>
      <div v-if="mode == ModeType.EDIT" class="editor__task-header">
        <span>{{ `<${task.type}>` }}</span>
        <button class="btn btn-danger" @click="removeTask(index)">remove task</button>
      </div>
      <div class="editor__task-container">
        <SingleChoiceTask
          @save-task="updateTask"
          v-if="task.type == TaskType.SINGLE_CHOICE"
          :task="(task as SingleChoice)"
          :mode="mode"
          :taskIndex="index"
          :saveTrigger="saveTrigger"
          :answer="getSingleChoiceAnswer(index)"
          :points="getTaskPoints(index)"
          :optionResults="getTaskResults(index)"
        />
        <MultipleChoiceTask
          @save-task="updateTask"
          v-if="task.type == TaskType.MULTIPLE_CHOICE"
          :task="(task as MultipleChoice)"
          :mode="mode"
          :taskIndex="index"
          :saveTrigger="saveTrigger"
          :answer="getMultipleChoiceAnswer(index)"
          :points="getTaskPoints(index)"
          :optionResults="getTaskResults(index)"
        />
      </div>
    </div>
    <div v-if="mode == ModeType.EDIT" class="editor__task-insert">
      <button class="btn btn-success" @click="insertSingleChoiceTask()">
        + single-choice
      </button>
      <button class="btn btn-success" @click="insertMultipleChoiceTask()">
        + multiple-choice
      </button>
    </div>
    <button
      v-if="mode == ModeType.RUN"
      class="btn btn-success"
      id="submit-button"
      @click="submitTest()"
    >
      Submit test
    </button>
  </div>
  <div class="space"></div>
</template>

<style scoped lang="scss">
.space {
  height: 200px;
}
.editor {
  max-width: 100%;
  display: inline-block;
  margin: 20px 0;
  padding: 5px;

  & h2 {
    font-size: 2.5rem;
  }

  & h3 {
    font-size: 1.5rem;
  }

  & button {
    font-size: 1rem;
    width: 150px;
  }

  &__field {
    display: flex;
    flex-direction: column;
    margin-bottom: 10px;

    & label {
      font-size: 1.5rem;
      font-style: italic;
      margin-bottom: 5px;
    }
  }

  &__option-edit {
    display: flex;
    flex-direction: row;
  }

  &__task-insert {
    display: block;
    height: auto;

    & button {
      font-size: 1rem;
      width: 170px;
      margin: 10px 10px 10px 0;
    }
  }

  &__task {
    margin-bottom: 20px;

    &-header {
      margin-top: 20px;
      margin-bottom: 5px;
    }
  }

  &__task-tag {
    width: 200px;
    overflow-wrap: break-word;
    word-wrap: break-word;
    word-break: break-word;
  }

  &__task-header {
    width: 90%;
    display: flex;
    flex-direction: row;
    justify-content: space-between;

    button {
      width: 170px;
    }
  }
}

#submit-button {
  width: 300px;
  height: 4rem;
  font-size: 2rem;
}
.control {
  position: fixed;
  bottom: 0;
  left: 0;
  z-index: 3;
  padding: 0;
  width: 100%;
  background: white;
  display: block;

  & button {
    font-size: 1rem;
    width: 150px;
    margin: 10px;
  }
}

.student-results {
  & h2 {
    font-size: 1.5rem;
  }

  &__passed {
    color: green;
  }

  &__failed {
    color: red;
  }
}
</style>
