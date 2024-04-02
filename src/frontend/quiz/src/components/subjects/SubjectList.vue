<script setup lang="ts">
import { ref, onMounted } from "vue";
import axios from "axios";

import { useSessionStore } from "@/stores/SessionStore";
import { BASE_URL } from "@/constants/constants";
import type { SubjectInfo } from "@/types/SubjectTypes";
import { Role, type UserInfo } from "@/types/UserTypes";
import { ModeType } from "@/types/OtherTypes";

const session = useSessionStore();

const emit = defineEmits(["subjectContainer"]);

const props = defineProps<{
  mode: ModeType;
}>();

const mode = ref(props.mode as ModeType);

const mySubjectsInfo = ref([] as Array<SubjectInfo>);
const mySubjectsOwners = ref([] as Array<string>);
const allSubjectsInfo = ref([] as Array<SubjectInfo>);

const subjectInfoTemp = ref({} as SubjectInfo);
const tempOwner = ref("" as string);
const accessCode = ref("" as string);

onMounted(async () => {
  if (session.userInfo !== null) {
    await fetchAllSubjectsInfo();
    await fetchMySubjectsInfo();
  }
});

const fetchMySubjectsInfo = async () => {
  if (session.userInfo?.role !== Role.ADMIN) {
    await axios
      .request({
        method: "GET",
        url: BASE_URL + "/frontend_api/get_my_subjects_info",
        headers: { Authorization: "Bearer " + session.userInfo?.token },
        timeout: 10000,
      })
      .then((response) => {
        mySubjectsInfo.value = (response.data as Array<string>).map((jsonStr) =>
          JSON.parse(jsonStr)
        ) as Array<SubjectInfo>;
        console.log("fetched my subjects");
      })
      .catch((err) => {
        const errorMessage = err.response.data as Array<string>;
        console.log("Error: " + errorMessage[0] + " Reason: " + errorMessage[1]);
        session.alertError(errorMessage[0], errorMessage[1]);
      });
  } else if (session.userInfo?.role === Role.ADMIN) {
    await fetchAllSubjectsInfo();
    mySubjectsInfo.value = allSubjectsInfo.value;
  }
  // fetch mu subjects owner names
  mySubjectsOwners.value = [];
  for (const info of mySubjectsInfo.value) {
    await fetchSubjectOwner(info.owner);
    mySubjectsOwners.value.push(tempOwner.value);
  }
};

const fetchAllSubjectsInfo = async () => {
  await axios
    .request({
      method: "GET",
      url: BASE_URL + "/frontend_api/get_all_subjects_info",
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      timeout: 10000,
    })
    .then((response) => {
      allSubjectsInfo.value = (response.data as Array<string>).map((jsonStr) =>
        JSON.parse(jsonStr)
      ) as Array<SubjectInfo>;
      console.log("fetched all subjects");
    })
    .catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log("Error: " + errorMessage[0] + " Reason: " + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1]);
    });
};

const deleteSubject = async (subjectId: string) => {
  await axios
    .request({
      method: "DELETE",
      url: BASE_URL + "/frontend_api/delete_subject/" + subjectId,
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      timeout: 10000,
    })
    .then((response) => {
      console.log("subject deleted!");
    })
    .catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log("Error: " + errorMessage[0] + " Reason: " + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1]);
    });
  await fetchMySubjectsInfo();
};

const subscribe = async () => {
  let formData = new FormData();
  formData.append("access_code", JSON.stringify(accessCode.value));
  let postURL = BASE_URL + "/frontend_api/subject_subscribe";
  if (session.userInfo?.role == Role.TEACHER) postURL += "_teacher/";
  if (session.userInfo?.role == Role.STUDENT) postURL += "_student/";
  await axios
    .request({
      method: "POST",
      url: postURL + subjectInfoTemp.value.id,
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      data: formData,
      timeout: 10000,
    })
    .then((response) => {
      console.log("subscribed for the subject!");
    })
    .catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log("Error: " + errorMessage[0] + " Reason: " + errorMessage[1]);
      session.alertError(errorMessage[0], errorMessage[1]);
    });
  await fetchMySubjectsInfo();
};

const createSubject = async () => {
  emit("subjectContainer", null, ModeType.EDIT);
};

const setMode = (modeValue: ModeType) => {
  mode.value = modeValue;
};

const fetchSubjectOwner = async (ownerUsername: string) => {
  await axios
    .request({
      method: "GET",
      url: BASE_URL + "/frontend_api/get_user_info/" + ownerUsername,
      headers: { Authorization: "Bearer " + session.userInfo?.token },
      timeout: 10000,
    })
    .then((response) => {
      console.log('here')
      console.log((response.data as UserInfo).name)
      tempOwner.value = (response.data as UserInfo).name;
    })
    .catch((err) => {
      const errorMessage = err.response.data as Array<string>;
      console.log("Error: " + errorMessage[0] + " Reason: " + errorMessage[1]);
      tempOwner.value = ownerUsername;
    });
};
</script>

<template>
  <div class="subscriber" v-if="session.userInfo?.role !== Role.ADMIN">
    <h1 class="page-title">Subscribe for subject:</h1>
    <table>
      <tbody>
        <tr>
          <td>Find subject:</td>
          <td>
            <div>
              <select
                v-model="subjectInfoTemp"
                id="subject-selector"
                class="publisher__subject-selector form-select"
              >
                <option
                  v-for="(info, index) in allSubjectsInfo"
                  :key="info.id"
                  :value="info"
                >
                  {{ info.name }}
                </option>
              </select>
            </div>
          </td>
        </tr>
        <tr>
          <td>Subject name:</td>
          <td>{{ subjectInfoTemp?.name }}</td>
        </tr>
        <tr>
          <td>Subject description:</td>
          <td class="publisher__description">{{ subjectInfoTemp?.description }}</td>
        </tr>
        <tr>
          <td>Access Code:</td>
          <input
            class="form-control subscriber__access-code"
            placeholder="code from your teacher"
            v-model="accessCode"
          />
        </tr>
      </tbody>
    </table>
    <button class="btn btn-primary" @click="subscribe">Subscribe</button>
  </div>
  <div class="control">
    <button
      class="btn btn-primary"
      v-if="
        (mode == ModeType.EDIT || mode == ModeType.VIEW) &&
        session.userInfo?.role !== Role.ADMIN
      "
      @click="createSubject"
    >
      Create Subject
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
  </div>
  <div class="subject-list">
    <h1 class="page-title">Choose subject:</h1>
    <div
      class="subject"
      v-for="(info, index) in mySubjectsInfo"
      :key="info.name + info.description"
      @click="$emit('subjectContainer', info.id, mode)"
    >
      <h3>
        <span>{{ info.name ? info.name : "No name" }}</span>
        <button
          v-if="mode == ModeType.EDIT"
          class="btn btn-danger"
          @click.stop="deleteSubject(info.id)"
        >
          Delete
        </button>
      </h3>
      <table>
        <tbody>
          <tr>
            <td>Description:</td>
            <td class="subject__description">
              {{ info.description ? info.description : "-" }}
            </td>
          </tr>
          <tr>
            <td>Owner:</td>
            <td>{{ mySubjectsOwners[index] ? mySubjectsOwners[index] : "-" }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped lang="scss">
.subscriber {
  min-width: 350px;
  max-width: 100%;
  font-size: 1rem;
  margin-bottom: 80px;

  & table {
    border-collapse: separate;
    border-spacing: 10px 10px;
    margin: 10px 0;

    & td:nth-child(1) {
      width: 120px;
      font-style: italic;
      overflow-wrap: break-word;
      word-wrap: break-word;
      word-break: break-word;
    }

    & td:nth-child(2) {
      overflow-wrap: break-word;
      word-wrap: break-word;
      word-break: break-word;
    }

    select,
    input {
      width: 200px;
    }
  }

  button {
    font-size: 1rem;
    width: 150px;
    margin: 10px 0;
  }
}
.control {
  z-index: 3;
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background: white;
  display: block;

  & button {
    font-size: 1rem;
    width: 150px;
    margin: 10px;
  }
}

.subject-list {
  padding-bottom: 100px;

  & h3 {
    display: flex;
    justify-content: space-between;

    & span {
      margin-right: 30px;
    }

    & button:hover {
      border: 3px solid white;
    }
  }
}
.subject {
  display: inline-block;
  max-width: 100%;
  min-width: 320px;
  margin: 10px;
  font-size: 1rem;
  border: 3px solid blue;
  border-radius: 10px;
  padding: 20px;

  & table {
    border-collapse: separate;
    border-spacing: 10px 10px;

    & td {
      vertical-align: top;
    }

    & td:first-child {
      font-style: italic;
    }

    & td:nth-child(2) {
      overflow-wrap: break-word;
      word-wrap: break-word;
      word-break: break-word;
    }
  }

  &:hover {
    background: blue;
    color: white;
    transition: 0.3s;
    cursor: pointer;
  }
}
</style>
