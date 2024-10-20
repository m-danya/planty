<template>
  <div class="section">
    <h2>{{ section.title }}</h2>
    <TaskComponent
      v-for="task in section.tasks"
      :key="task.id"
      :task="task"
      @toggleTaskCompletion="toggleTaskCompletion"
      @taskClicked="onTaskClicked"
      @taskUpdated="onTaskUpdated"
    />
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from "vue";
import TaskComponent from "./TaskComponent.vue";

defineProps({
  section: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits([
  "shuffleSection",
  "taskMoved",
  "toggleTaskCompletion",
  "taskClicked",
  "taskUpdated",
]);

const toggleTaskCompletion = (task) => {
  emit("toggleTaskCompletion", task);
};

const onTaskClicked = (task) => {
  emit("taskClicked", task);
};

const onTaskUpdated = (updatedTask) => {
  emit("taskUpdated", updatedTask);
};
</script>

<style scoped>
.section {
  width: calc(50% - 40px);
  margin-right: 20px;
  margin-bottom: 30px;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.section:nth-child(2n) {
  margin-right: 0;
}

.section:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

h2 {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 15px;
  color: #343a40;
}

.shuffle-button {
  background-color: transparent;
  border: none;
  font-size: 18px;
  cursor: pointer;
}

.tasks {
  min-height: 50px;
  padding-left: 0;
  list-style: none;
}

.handle {
  float: left;
  padding-top: 8px;
  padding-bottom: 8px;
}
</style>
