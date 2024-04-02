<script setup lang="ts">
import { ref, onMounted, toRaw, watch } from "vue";

import type { SingleChoice } from "@/types/TestTypes";
import { ModeType } from "@/types/OtherTypes";

const props = defineProps<{
  task: SingleChoice;
  mode: ModeType;
  taskIndex: number;
  saveTrigger: boolean;
  answer: null | number;
  points: null | number;
  optionResults: null | Array<number>;
}>();
const emit = defineEmits(["saveTask"]);

const task = ref({} as SingleChoice);

onMounted(() => {
  task.value = structuredClone(toRaw(props.task) as SingleChoice);
  if (props.answer !== null && props.mode == ModeType.STUDENT_RESULTS) {
    task.value.answer = props.answer;
  }
  if (props.mode == ModeType.RUN || props.mode == ModeType.RESULTS) {
    task.value.answer = -1;
  }
});

watch(
  () => props.saveTrigger,
  (newTrigger) => {
    if (newTrigger) {
      emit("saveTask", props.taskIndex, task.value as SingleChoice);
    }
  }
);

// buttons

const removeOption = (optionIndex: number) => {
  // modify answer (index)
  if (optionIndex <= task.value.answer) {
    if (optionIndex == task.value.answer) {
      task.value.answer = 0;
    } else {
      task.value.answer--;
    }
  }
  task.value.options.splice(optionIndex, 1);
};

const insertOption = (optionIndex: number = -1) => {
  // insert an empty option
  if (optionIndex == -1) {
    task.value.options.push("");
  } else {
    // modify answer (index)
    if (optionIndex <= task.value.answer) {
      task.value.answer++;
    }
    // insert
    task.value.options.splice(optionIndex, 0, "");
  }
};

const getOptionResult = (optionIndex: number) => {
  if (props.optionResults !== null) return Math.round(props.optionResults[optionIndex]);
  return null;
};
</script>

<template>
  <div class="task">
    <h3 class="task__header">
      <span>#{{ props.taskIndex + 1 }}</span>
      <div class="task__header-tag">
        <span v-if="props.mode != ModeType.EDIT">{{ task.tag }}</span>
        <input
          v-if="props.mode == ModeType.EDIT"
          class="form-control"
          placeholder="a task tag"
          v-model="task.tag"
        />
      </div>
      <div class="task__header-points">
        <span v-if="props.mode == ModeType.STUDENT_RESULTS"
          >{{ props.points?.toFixed(1) }} /</span
        >
        <span v-if="props.mode != ModeType.EDIT">{{ task.points }}</span>
        <input
          v-if="props.mode == ModeType.EDIT"
          class="form-control"
          type="number"
          min="0"
          v-model="task.points"
        />
        <span>points</span>
      </div>
    </h3>
    <p class="task__question" v-if="props.mode != ModeType.EDIT">{{ task.question }}</p>
    <div v-if="props.mode == ModeType.EDIT" class="task__field">
      <textarea
        v-model="task.question"
        class="form-control task__question"
        id="task-question"
        placeholder="enter a task question"
      />
    </div>
    <div v-for="(option, optionIndex) in task.options" :key="optionIndex">
      <div class="task__field">
        <button
          v-if="props.mode == ModeType.EDIT"
          class="btn btn-primary"
          @click="insertOption(optionIndex)"
        >
          +
        </button>
        <div class="task__option">
          <div
            v-if="
              props.mode == ModeType.RESULTS || props.mode == ModeType.ANSWERS_RESULTS
            "
            class="task__option-result"
          >
            {{ getOptionResult(optionIndex) }}%
          </div>
          <input
            v-model="task.answer"
            class="form-check-input"
            :id="`input-id-` + props.taskIndex + `-` + optionIndex"
            type="radio"
            :value="optionIndex"
            :disabled="props.mode != ModeType.EDIT && props.mode != ModeType.RUN"
          />
          <label
            :for="`input-id-` + props.taskIndex + `-` + optionIndex"
            v-if="props.mode != ModeType.EDIT"
            >{{ option }}</label
          >
          <textarea
            v-model="task.options[optionIndex]"
            v-if="props.mode == ModeType.EDIT"
            class="form-control"
            placeholder="enter an answer option"
          />
          <button
            v-if="props.mode == ModeType.EDIT"
            class="btn btn-danger"
            @click="removeOption(optionIndex)"
          >
            X
          </button>
        </div>
      </div>
    </div>
    <button
      v-if="props.mode == ModeType.EDIT"
      class="btn btn-primary"
      @click="insertOption()"
    >
      +
    </button>
  </div>
</template>

<style scoped lang="scss">
.task {
  box-sizing: border-box;
  border: 2px lightgray solid;
  padding: 10px;
  min-width: 330px;

  &__question {
    font-size: 1.2rem;
  }

  &__header {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;

    & span,
    & input {
      font-size: 1rem;
      margin-right: 5px;
    }

    &-tag {
      width: auto;
    }

    &-points {
      display: flex;

      & input {
        width: 80px;
        margin-right: 5px;
      }
    }
  }

  & button {
    font-size: 1rem;
    width: 100px;
    height: 40px;
    margin: 5px;
    margin-left: 15px;
  }

  &__field {
    display: flex;
    flex-direction: column;
    margin-bottom: 5px;

    & label {
      font-size: 1.5rem;
      margin-bottom: 5px;
    }

    & textarea {
      width: auto;
      height: 1lh;
    }

    & #task-question {
      height: 3lh;
    }
  }

  &__option {
    display: flex;
    flex-direction: row;
    align-items: center;
    width: auto;
    margin: 5px 0;
    overflow-wrap: break-word;
    word-wrap: break-word;
    word-break: break-word;

    & input {
      height: 40px;
      width: 40px;
      color: orange;
      margin-right: 5px;
    }

    &-result {
      width: 50px;
      margin-right: 10px;
      font-size: 1.2rem;
    }
  }
}
</style>
