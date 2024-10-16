<template>
  <div class="task" :id="task.id" @click="onTaskClick">
    <div class="task-header">
      <button class="complete-button" @click.stop="emitToggleTaskCompletion">
        <span v-if="task.is_completed">✔️</span>
      </button>
      <div
        :class="{ 'task-title': true, is_completed: task.is_completed }"
        @click.stop="onTitleClick"
      >
        <template v-if="isEditing">
          <input
            v-model="editedTitle"
            @keyup.enter="updateTaskTitle"
            @blur="cancelEditing"
            ref="titleInput"
          />
        </template>
        <template v-else>
          {{ task.title }}
        </template>
      </div>
    </div>
    <div class="task-description">{{ task.description }}</div>
    <div class="task-date" v-if="task.due_to">
      Due: {{ formatDate(task.due_to) }}
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from "vue";
import { defineProps, defineEmits } from "vue";

import axios from "axios";

const props = defineProps({
  task: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits([
  "toggleTaskCompletion",
  "taskClicked",
  "taskUpdated",
]);

const isEditing = ref(false);
const editedTitle = ref(props.task.title);
const titleInput = ref(null);

const formatDate = (dateStr) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString();
};

const emitToggleTaskCompletion = () => {
  emit("toggleTaskCompletion", props.task);
};

const onTaskClick = () => {
  emit("taskClicked", props.task);
};

const onTitleClick = (event) => {
  if (event.altKey) {
    isEditing.value = true;
    nextTick(() => {
      titleInput.value.focus();
    });
  } else {
    onTaskClick();
  }
};

const updateTaskTitle = async () => {
  try {
    const requestData = {
      id: props.task.id,
      title: editedTitle.value,
    };
    const response = await axios.patch("/api/task", requestData);
    const updatedTask = response.data.task;
    emit("taskUpdated", updatedTask);
  } catch (error) {
    console.error("Error while updating task title:", error);
  } finally {
    isEditing.value = false;
  }
};

const cancelEditing = () => {
  isEditing.value = false;
  editedTitle.value = props.task.title;
};
</script>

<style scoped>
.task {
  padding: 15px 20px;
  border: 1px solid #ddd8d8;
  margin-bottom: 15px;
  background-color: #ffffff;
  border-radius: 8px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
}

.task:hover {
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.05);
}

.task-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.complete-button {
  width: 28px;
  height: 28px;
  background-color: transparent;
  border: 2px solid #28a745;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.complete-button:hover {
  background-color: #28a745;
  color: #fff;
}

.task-title {
  font-size: 18px;
  font-weight: 600;
  color: #495057;
  flex-grow: 1;
  margin-left: 15px;
  transition: color 0.3s ease, text-decoration 0.3s ease;
  cursor: pointer;
}

.task-title.is_completed {
  text-decoration: line-through;
  color: #6c757d;
}

.task-title input {
  width: 100%;
  font-size: 18px;
  font-weight: 600;
  border: none;
  outline: none;
}

.task-description {
  margin-top: 10px;
  font-size: 14px;
  color: #868e96;
}

.task-date {
  margin-top: 10px;
  font-size: 14px;
  color: #adb5bd;
  text-align: right;
}

.task-date::before {
  content: "📅 ";
}
</style>
