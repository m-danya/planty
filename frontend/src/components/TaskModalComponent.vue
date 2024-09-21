<template>
  <div class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <h2>{{ task.title }}</h2>
      <p>{{ task.description }}</p>
      <p v-if="task.due_to">Due: {{ formatDate(task.due_to) }}</p>
      <button @click="closeModal">Close</button>
    </div>
  </div>
</template>

<script setup>
import { defineEmits, defineProps } from "vue";
defineProps({
  task: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["close"]);

const formatDate = (dateStr) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString();
};

const closeModal = () => {
  emit("close");
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
}

.modal-content h2 {
  font-size: 24px;
  margin-bottom: 15px;
}

.modal-content p {
  font-size: 16px;
  margin-bottom: 10px;
}

.modal-content button {
  margin-top: 20px;
  padding: 10px 15px;
  font-size: 16px;
  background-color: #28a745;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.modal-content button:hover {
  background-color: #218838;
}
</style>
