<template>
  <div class="sections">
    <div
      class="section"
      v-for="section in sections"
      :key="section.id"
      :data-section-id="section.id"
    >
      <div class="section-header">
        <h2>{{ section.title }}</h2>
        <button class="shuffle-button" @click="shuffleSection(section.id)">
          🔀
        </button>
      </div>
      <draggable
        v-model="section.tasks"
        group="tasks"
        @end="onDragEnd"
        item-key="id"
        class="tasks"
      >
        <template #item="{ element: task }">
          <div class="task" :id="task.id">
            <div class="task-header">
              <button
                class="complete-button"
                @click="toggleTaskCompletion(task)"
              >
                <span v-if="task.is_completed">✔️</span>
              </button>
              <div
                :class="{ 'task-title': true, is_completed: task.is_completed }"
              >
                {{ task.title }}
              </div>
            </div>
            <div class="task-description">{{ task.description }}</div>
            <div class="task-date" v-if="task.due_to_next">
              Due: {{ formatDate(task.due_to_next) }}
            </div>
          </div>
        </template>
      </draggable>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import draggable from "vuedraggable";

const sections = ref([]);

const fetchSections = async () => {
  try {
    const response = await axios.get("/api/sections");
    sections.value = response.data;
  } catch (error) {
    console.error("Error fetching sections:", error);
  }
};

const shuffleSection = async (sectionId) => {
  try {
    const response = await axios.post("/api/section/shuffle", {
      section_id: sectionId,
    });
    const shuffledSection = response.data.section;
    const index = sections.value.findIndex(
      (section) => section.id === sectionId
    );
    sections.value[index].tasks = shuffledSection.tasks;
  } catch (error) {
    console.error("Error shuffling section:", error);
  }
};

const toggleTaskCompletion = async (task) => {
  task.is_completed = !task.is_completed;
  try {
    await axios.post("/api/task/toggle_completed", {
      task_id: task.id,
    });
  } catch (error) {
    console.error("Error updating task:", error);
  }
};

const onDragEnd = async (event) => {
  const movedTask = event.item;
  const newSectionElement = event.to.closest(".section");
  const newSectionId = newSectionElement?.dataset?.sectionId;

  const taskId = movedTask.id;
  const newIndex = event.newIndex;

  const requestData = {
    task_id: taskId,
    section_to_id: newSectionId,
    index: newIndex,
  };

  try {
    await axios.post("/api/task/move", requestData);
  } catch (error) {
    console.error("Error moving task:", error);
  }
};

const formatDate = (dateStr) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString();
};

onMounted(() => {
  fetchSections();
});
</script>

<style scoped>
.sections {
  display: flex;
  margin: 20px;
}

.section {
  margin-bottom: 30px;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
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
  font-size: 24px;
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
}

.task-title.is_completed {
  text-decoration: line-through;
  color: #6c757d;
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

.sections {
  gap: 20px;
}

.section {
  width: calc(50% - 40px);
  margin-right: 20px;
}

.section:nth-child(2n) {
  margin-right: 0;
}

h2 {
  font-size: 20px;
}

div {
  -webkit-text-size-adjust: 100%;
  font-feature-settings: normal;
  font-family: ui-sans-serif, -apple-system, system-ui, Segoe UI, Helvetica,
    Apple Color Emoji, Arial, sans-serif, Segoe UI Emoji, Segoe UI Symbol;
  font-variation-settings: normal;
  /* line-height: 1.5; */
  -moz-tab-size: 4;
  tab-size: 4;
}
</style>
