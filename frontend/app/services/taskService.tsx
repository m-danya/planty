import axios from "axios";

// TODO: use autogenerated types from openapi.json
export async function moveTask(taskData: {
  task_id: string;
  section_to_id: string;
  index: number;
}) {
  try {
    const response = await axios.post("/api/task/move", taskData);
    return response.data;
  } catch (error) {
    alert("Error while moving task, check the console for logs");
    console.error("Error while moving task:", error);
    throw error;
  }
}
