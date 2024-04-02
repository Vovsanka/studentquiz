<script setup lang="ts">
import { ref, reactive, onMounted, toRaw } from "vue";
import axios from "axios";

import { useSessionStore } from "@/stores/SessionStore";
import { BASE_URL } from "@/constants/constants";
import type { Subject, SubjectInfo } from "@/types/SubjectTypes";
import { ModeType } from "@/types/OtherTypes";
import type { TestInstance } from "@/types/TestTypes";
import { Role, type UserInfo } from "@/types/UserTypes";

const session = useSessionStore();

const emit = defineEmits(["close", "publish", "testinstance"]);

const props = defineProps<{
  subjectId: null | string;
  mode: ModeType;
}>();

const mode = ref(props.mode as ModeType)

const subject = reactive({
  info: {
    name: "",
    description: "",
    id: "",
  } as SubjectInfo,
  test_instances: [] as Array<TestInstance>,
} as Subject);

const subjectId = ref(props.subjectId as string)
const subjectOwner = ref({} as UserInfo);
const subjectTeachers = ref([] as Array<UserInfo>);
const subjectStudents = ref([] as Array<UserInfo>);

onMounted(async () => {
  await fetchSubject();
  await fetchSubjectOwner();
  await fetchSubjectTeachers();
  if (session.userInfo?.role == Role.TEACHER) {
    await fetchSubjectStudents();
  }
});

const fetchSubject = async () => {
  await axios
    .request({
      method: "GET",
      url:
        BASE_URL +
        "/frontend_api/get_subject" +
        (subjectId.value !== null ? "/" + subjectId.value : ""),
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      timeout: 10000,
    })
    .then((response) => {
      const fetchedSubject = response.data as Subject;
      subject.info = fetchedSubject.info;
      subject.students = fetchedSubject.students;
      subject.test_instances = fetchedSubject.test_instances;
      subject.student_access_code = fetchedSubject.student_access_code;
      subject.teacher_access_code = fetchedSubject.teacher_access_code;
      subjectId.value = subject.info.id
      console.log("subject fetched");
    }).catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log('Error: ' + errorMessage[0] + ' Reason: ' + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1])
    });
};

const saveSubject = async () => {
  let formData = new FormData();
  formData.append("subject", JSON.stringify(toRaw(subject)));
  await axios
    .request({
      method: "PUT",
      url:
        BASE_URL +
        "/frontend_api/save_subject/" + subjectId.value,
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      data: formData,
      timeout: 10000,
    })
    .then((response) => {
      console.log("subject saved");
    }).catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log('Error: ' + errorMessage[0] + ' Reason: ' + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1])
    });
};

const fetchSubjectOwner = async () => {
  await axios
    .request({
      method: "GET",
      url: BASE_URL + "/frontend_api/get_user_info/" + subject.info.owner,
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      timeout: 10000,
    })
    .then((response) => {
      subjectOwner.value = response.data as UserInfo;
      console.log("subject owner fetched");
    }).catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log('Error: ' + errorMessage[0] + ' Reason: ' + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1])
    });
};

const fetchSubjectTeachers = async () => {
  subjectTeachers.value = []
  await axios.all(subject.info.teachers.map((teacher) => {
    axios.request({
      method: "GET",
      url: BASE_URL + "/frontend_api/get_user_info/" + teacher,
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      timeout: 10000,
    })
    .then((response) => {
      subjectTeachers.value.push(response.data as UserInfo)
    }).catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log('Error: ' + errorMessage[0] + ' Reason: ' + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1])
    });
  }))
  console.log('subject teachers fetched')
};

const fetchSubjectStudents = async () => {
  subjectStudents.value = []
  await axios.all(subject.students.map((student) => {
    axios.request({
      method: "GET",
      url: BASE_URL + "/frontend_api/get_user_info/" + student,
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      timeout: 10000,
    })
    .then((response) => {
      subjectStudents.value.push(response.data as UserInfo)
    }).catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log('Error: ' + errorMessage[0] + ' Reason: ' + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1])
    });
  }))
  console.log('subject students fetched')
};

const close = async () => {
  if (mode.value != ModeType.RUN && session.userInfo?.role !== Role.ADMIN) {
    await saveSubject()
  }
  emit("close");
};

const setMode = (modeValue: ModeType) => {
  mode.value = modeValue;
};

const publishTest = async () => {
  await saveSubject();
  emit("publish", subject.info.id);
};

const openTestInstance = (testInstance : TestInstance) => {
  emit("testinstance", subject.info.id, testInstance);
};

const removeTeacher = async (teacherUsername : string) => {
  await axios
    .request({
      method: "DELETE",
      url: BASE_URL + "/frontend_api/remove_teacher_from_subject/" + subjectId.value + '/' + teacherUsername,
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      timeout: 10000,
    })
    .then((response) => {
      console.log("teacher removed");
    }).catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log('Error: ' + errorMessage[0] + ' Reason: ' + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1])
    });
  await fetchSubject()
  await fetchSubjectTeachers()
};

const removeStudent = async (studentUsername : string) => {
  await axios
    .request({
      method: "DELETE",
      url: BASE_URL + "/frontend_api/remove_student_from_subject/" + subjectId.value + '/' + studentUsername,
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      timeout: 10000,
    })
    .then((response) => {
      console.log("student removed");
    }).catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log('Error: ' + errorMessage[0] + ' Reason: ' + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1])
    });
  await fetchSubject()
  await fetchSubjectStudents()
};

const deleteTestInstancce = async (testInstance : TestInstance) => {
  await axios
    .request({
      method: "DELETE",
      url: BASE_URL +
        "/frontend_api/delete_test_instance/" +
        subjectId.value +
        "?test_id=" +
        testInstance.test.info.id +
        "&remark=" +
        testInstance.remark,
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      timeout: 10000,
    })
    .then((response) => {
      console.log("test instance deleted!");
    }).catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log('Error: ' + errorMessage[0] + ' Reason: ' + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1])
    });
  await fetchSubject();
};

const showCode = (event: Event) => {
  const el = event.target as HTMLElement;
  el.classList.add('subject__code--show')
}
</script>

<template>
  <div class="subject">
    <h2 v-if="mode != ModeType.EDIT">{{ subject?.info?.name }}</h2>
    <table>
      <tbody>
        <tr v-if="mode == ModeType.EDIT">
          <td><label for="subject-name">Subject: </label></td>
          <td>
            <input
              v-model="subject.info.name"
              class="form-control"
              id="sujbect-name"
              placeholder="enter a subject name"
            />
          </td>
        </tr>
        <tr>
          <td><label for="subject-description">Description: </label></td>
          <td class="subject__description">
            <div v-if="mode != ModeType.EDIT">{{ subject?.info?.description }}</div>
            <div v-if="mode == ModeType.EDIT">
              <textarea
                v-model="subject.info.description"
                class="form-control"
                id="sujbect-description"
                placeholder="enter a subject description"
              />
            </div>
          </td>
        </tr>
        <tr>
          <td>Owner:</td>
          <td>{{ subjectOwner.name }}</td>
        </tr>
        <tr>
          <td>Teachers:</td>
          <td>
            <ul>
              <li v-for="(teacher, index) in subjectTeachers" :key="index">
                <div
                  v-if="teacher.name != subjectOwner.name"
                  class="subject__teacher-username"
                >
                  <span class="subject__teacher">
                    {{ teacher.name }}
                  </span>
                  <button
                    class="btn btn-danger"
                    v-if="mode == ModeType.EDIT && session.userInfo?.role == Role.TEACHER"
                    @click="removeTeacher(teacher.username)"
                  >
                    X
                  </button>
                </div>
              </li>
            </ul>
          </td>
        </tr>
        <tr v-if="mode != ModeType.RUN">
          <td><label for="teacher-code">Teacher code: </label></td>
          <td v-if="mode == ModeType.VIEW" class="subject__code" @click="showCode">
            {{ subject.teacher_access_code }}
          </td>
          <td v-if="mode == ModeType.EDIT">
            <input
              v-model="subject.teacher_access_code"
              class="form-control"
              id="teacher-code"
            />
          </td>
        </tr>
        <tr v-if="mode != ModeType.RUN">
          <td><label for="student-code">Student code: </label></td>
          <td v-if="mode == ModeType.VIEW" class="subject__code" @click="showCode">
            {{ subject.student_access_code }}
          </td>
          <td v-if="mode == ModeType.EDIT">
            <input
              v-model="subject.student_access_code"
              class="form-control"
              id="student-code"
            />
          </td>
        </tr>
      </tbody>
    </table>

    <div
      v-for="(testInstance, index) in subject.test_instances"
      :key="index"
      class="subject__test-instance"
      @click="openTestInstance(testInstance)"
    >
      <h2>
        <span>{{
          testInstance.test.info.name ? testInstance.test.info.name : "No name"
        }}</span>
        <button
          v-if="mode == ModeType.EDIT"
          class="btn btn-danger"
          @click.stop="deleteTestInstancce(testInstance)"
        >
          Delete
        </button>
      </h2>
      <table>
        <tbody>
          <tr>
            <td>Description:</td>
            <td>
              {{ testInstance.test.info.description }}
            </td>
          </tr>
          <tr>
            <td>Publish remark:</td>
            <td>{{ testInstance.remark }}</td>
          </tr>
          <tr v-if="mode != ModeType.RUN">
            <td>Published by:</td>
            <td>
              {{ testInstance.published_by }}
            </td>
          </tr>
          <tr v-if="mode != ModeType.RUN">
            <td>Published at:</td>
            <td>
              {{ new Date(testInstance.published_at).toLocaleString() }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="session.userInfo?.role == Role.TEACHER" class="subject__students">
      <h3 style="font-weight: bold">Students:</h3>
      <table>
        <thead>
          <tr>
            <th style="font-weight: bold">Name</th>
            <th style="font-weight: bold">Username</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(student, index) in subjectStudents" :key="index">
            <td>
              <ul>
                <li>
                  <div>
                    <span class="subject__teacher">
                      {{ student.name }}
                    </span>
                  </div>
                </li>
              </ul>
            </td>
            <td>
              <ul>
                <li>
                  <div class="subject__teacher-username">
                    <span>
                      {{ student.username }}
                    </span>
                    <button
                      class="btn btn-danger"
                      v-if="mode == ModeType.EDIT"
                      @click="removeStudent(student.username)"
                    >
                      X
                    </button>
                  </div>
                </li>
              </ul>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  <div class="control">
    <button class="btn btn-danger" @click="close()">
      Return
      <span v-if="mode != ModeType.RUN && session.userInfo?.role === Role.TEACHER"
        >(save)</span
      >
    </button>
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
      v-if="
        (mode == ModeType.EDIT || mode == ModeType.VIEW) &&
        session.userInfo?.role === Role.TEACHER
      "
      class="btn btn-success"
      @click="publishTest()"
    >
      {{ "Save & Publish" }}
    </button>
  </div>
  <div class="space"></div>
</template>

<style scoped lang="scss">
.space {
  height: 260px;
}
.subject {
  min-width: 350px;
  font-size: 1.2rem;
  border: 3px solid blue;
  padding: 20px;

  & h2 {
    font-size: 2.5rem;
  }

  & table {
    min-width: 250px;
    border-collapse: separate;
    border-spacing: 10px 10px;
    margin-bottom: 10px;

    & td {
      vertical-align: center;
      text-align: left;
      max-width: 700px;
      overflow-wrap: break-word;
      word-wrap: break-word;
      word-break: break-word;
    }

    & td:first-child {
      font-style: italic;
      width: 120px;
    }

    & h3 {
      font-size: 1.5rem;
    }
  }

  & ul {
    margin: 0;
    padding: 0;
  }

  &__add-teacher {
    margin-bottom: 10px;
    display: flex;
    flex-direction: row;
    justify-content: space-between;

    & button {
      padding: 10px;
      width: 200px;
      margin-left: 10px;
    }
  }

  &__code {
    border: 1px solid purple;
    color: transparent;
    border-radius: 3px;

    &--show {
      border: none;
      color: black;
    }
  }

  &__teacher-username {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 5px 0;

    & button {
      margin: 5px;
    }
  }

  &__test-instance {
    box-sizing: border-box;
    max-width: 90vw;
    min-width: 300px;
    display: inline-block;
    margin: 10px;
    font-size: 1rem;
    border: 3px solid orangered;
    border-radius: 10px;
    padding: 10px;

    & h2 {
      display: flex;
      justify-content: space-between;
      font-size: 2rem;

      & span {
        margin-right: 30px;
      }

      & button:hover {
        border: 3px solid white;
      }
    }

    & table {
      border-collapse: separate;
      border-spacing: 10px 10px;

      & td {
        vertical-align: center;
      }

      & td:first-child {
        font-style: italic;
        width: 120px;
        overflow-wrap: break-word;
        word-wrap: break-word;
        word-break: break-word;
      }

      & td:nth-child(2) {
        overflow-wrap: break-word;
        word-wrap: break-word;
        word-break: break-word;
      }
    }

    &:hover {
      background: orangered;
      color: white;
      transition: 0.3s;
      cursor: pointer;
    }
  }

  &__students {
    margin-top: 50px;

    & h3 {
      margin-left: 10px;
    }
  }
}

.control {
  box-sizing: border-box;
  width: 100vw;
  position: fixed;
  bottom: 0;
  left: 0;
  background: white;
  display: block;

  & button {
    font-size: 1rem;
    width: 150px;
    margin: 10px;
    vertical-align: center;
  }
}
</style>
