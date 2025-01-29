import { Api, RecurrenceInfo, TaskUpdateRequest } from "@/api/Api";

const api = new Api().api;

export async function toggleTaskCompleted(taskId: string) {
  try {
    const result = await api.toggleTaskCompletedApiTaskToggleCompletedPost({
      task_id: taskId,
    });
    console.log("Toggled task completion successfully:", result);
    return result;
  } catch (error) {
    console.error("Failed to toggle task completion:", error);
    alert("Failed to toggle task completion");
    throw error;
  }
}

export async function toggleTaskArchived(taskId: string) {
  try {
    const result = await api.toggleTaskArchivedApiTaskToggleArchivedPost({
      task_id: taskId,
    });
    console.log("Toggled task archived status successfully:", result);
    return result;
  } catch (error) {
    console.error("Failed to toggle task archived status:", error);
    alert("Failed to toggle task archived status");
    throw error;
  }
}

export async function moveTask(
  taskId: string,
  sectionId: string,
  index: number
) {
  try {
    const result = await api.moveTaskApiTaskMovePost({
      task_id: taskId,
      section_to_id: sectionId,
      index: index,
    });
    console.log("Task moved successfully:", result);
    return result;
  } catch (error) {
    console.error("Failed to move task:", error);
    throw error;
  }
}

export async function updateTask(updateTaskData: TaskUpdateRequest) {
  try {
    const result = await api.updateTaskApiTaskPatch(updateTaskData);
    console.log("Task edited successfully:", result);
    return result;
  } catch (error: any) {
    console.error("Failed to edit task:", error);
    alert(
      `Error while editing task: ${
        error.response?.data?.detail || error.message
      }`
    );
    throw error;
  }
}

export async function createTask(
  sectionId: string,
  task: {
    title: string;
    description: string;
    due_to: string | null;
    recurrence: RecurrenceInfo | null;
  }
) {
  try {
    const result = await api.createTaskApiTaskPost({
      section_id: sectionId,
      title: task.title,
      description: task.description,
      due_to: task.due_to,
      recurrence: task.recurrence,
    });
    console.log("Task added successfully:", result);
    return result;
  } catch (error: any) {
    console.error("Failed to add task:", error);
    alert(
      `Failed to add task: ${error.response?.data?.detail || error.message}`
    );
    throw error;
  }
}
