<template>
  <div class="sections">
    <SectionComponent
      v-for="section in sections"
      :key="section.id"
      :section="section"
      @shuffleSection="shuffleSection"
      @taskMoved="onTaskMoved"
      @toggleTaskCompletion="toggleTaskCompletion"
      @taskClicked="onTaskClicked"
      @taskUpdated="onTaskUpdated"
    />
    <TaskModalComponent
      v-if="selectedTask"
      :task="selectedTask"
      @close="selectedTask = null"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import SectionComponent from "./components/SectionComponent.vue";
import TaskModalComponent from "./components/TaskModalComponent.vue";

const sections = ref([]);
const selectedTask = ref(null);

const fetchSections = async () => {
  try {
    const response = await axios.get("/api/sections");
    sections.value = response.data;
  } catch (error) {
    console.error("Error while getting sections:", error);
  }
};

const shuffleSection = async (sectionId) => {
  try {
    const response = await axios.post("/api/section/shuffle", {
      section_id: sectionId,
    });
    const shuffledSection = response.data;
    const index = sections.value.findIndex(
      (section) => section.id === sectionId
    );
    sections.value[index].tasks = shuffledSection.tasks;
  } catch (error) {
    console.error("Error while shuffling section:", error);
  }
};

const toggleTaskCompletion = async (task) => {
  try {
    const response = await axios.post("/api/task/toggle_completed", {
      task_id: task.id,
    });
    task.is_completed = response.data.is_completed;
  } catch (error) {
    console.error("Error while toggling task completion:", error);
  }
};

const onTaskMoved = async (payload) => {
  const { taskId, newSectionId, newIndex } = payload;
  const requestData = {
    task_id: taskId,
    section_to_id: newSectionId,
    index: newIndex,
  };
  try {
    await axios.post("/api/task/move", requestData);
  } catch (error) {
    console.error("Error while moving the task:", error);
  }
};

const onTaskClicked = (task) => {
  selectedTask.value = task;
};

const onTaskUpdated = (updatedTask) => {
  console.log(updatedTask);
  // Find the section containing the task
  const section = sections.value.find((sec) =>
    sec.tasks.some((task) => task.id === updatedTask.id)
  );
  if (section) {
    const taskIndex = section.tasks.findIndex(
      (task) => task.id === updatedTask.id
    );
    if (taskIndex !== -1) {
      // Update the task in the sections array
      section.tasks[taskIndex] = updatedTask;
    }
  }
};

onMounted(() => {
  fetchSections();
});
</script>

<style scoped>
.sections {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  margin: 20px;
}

div {
  -webkit-text-size-adjust: 100%;
  font-feature-settings: normal;
  font-family: ui-sans-serif, -apple-system, system-ui, Segoe UI, Helvetica,
    Apple Color Emoji, Arial, sans-serif, Segoe UI Emoji, Segoe UI Symbol;
  font-variation-settings: normal;
  -moz-tab-size: 4;
  tab-size: 4;
}
</style>
