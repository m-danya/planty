"use client";

import { Api, RecurrenceInfo } from "@/api/Api";
import { AddTaskDialog } from "@/components/tasks/add-task-dialog";
import { Task } from "@/components/tasks/task";
import { useSection } from "@/hooks/use-section";
import {
  closestCenter,
  DndContext,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

export function Section({ sectionId }: { sectionId: string }) {
  const {
    section,
    isLoading,
    isError,
    mutate: mutateSection,
  } = useSection(sectionId);
  const tasksFillers = Array.from({ length: 5 }, (_, index) => ({
    id: index,
  }));
  const [tasks, setTasks] = useState(tasksFillers);
  const api = new Api().api;

  const [isAddTaskDialogOpen, setIsAddTaskDialogOpen] = useState(false);

  useEffect(() => {
    if (section?.tasks) {
      setTasks(section.tasks);
    }
  }, [section]);

  const dndSensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 1 } })
  );

  async function handleToggleTaskCompleted(task_id: string) {
    try {
      const result = await api.toggleTaskCompletedApiTaskToggleCompletedPost({
        task_id: task_id,
      });
      console.log("Toggled task completion successfully:", result);
      mutateSection();
    } catch (error) {
      console.error("Failed to toggle task completion:", error);
      alert("Failed to toggle task completion");
    }
  }

  async function handleToggleTaskArchived(task_id: string) {
    try {
      const result = await api.toggleTaskArchivedApiTaskToggleArchivedPost({
        task_id: task_id,
      });
      console.log("Toggled task archived status successfully:", result);
      mutateSection();
    } catch (error) {
      console.error("Failed to toggle task archived status:", error);
      alert("Failed to toggle task archived status");
    }
  }

  async function handleDragEnd(event: any) {
    const { active, over } = event;
    // if (!over) return;
    const oldIndex = tasks.findIndex((task) => task.id === active.id);
    const newIndex = tasks.findIndex((task) => task.id === over.id);

    if (active.id !== over.id) {
      setTasks((tasks) => {
        return arrayMove(tasks, oldIndex, newIndex);
      });

      try {
        const result = await api.moveTaskApiTaskMovePost({
          task_id: active.id,
          section_to_id: sectionId,
          index: newIndex,
        });
        console.log("Task moved successfully:", result);
      } catch (error) {
        console.error("Failed to move task:", error);
        alert("Failed to move task");
      }
    }
  }

  async function handleTaskEdit(updateTaskData: {
    id: string;
    title?: string;
    description?: string;
    due_to?: string;
    recurrence: RecurrenceInfo | null;
  }) {
    try {
      const result = await api.updateTaskApiTaskPatch({
        id: updateTaskData.id,
        title: updateTaskData.title,
        description: updateTaskData.description,
        due_to: updateTaskData.due_to,
        recurrence: updateTaskData.recurrence,
      });
      console.log("Task edited successfully:", result);
    } catch (error) {
      console.error("Failed to edit task:", error);
      alert(`Error while editing task: ${error.response.data.detail}`);
    }
    mutateSection();
  }

  async function handleTaskAdd(task: {
    title: string;
    description: string;
    due_to: string | null;
    recurrence: RecurrenceInfo | null;
  }) {
    try {
      const result = await api.createTaskApiTaskPost({
        section_id: sectionId,
        title: task.title,
        description: task.description,
        due_to: task.due_to,
        recurrence: task.recurrence,
      });
      console.log("Task added successfully:", result);
      mutateSection();
    } catch (error) {
      console.error("Failed to add task:", error);
      alert(`Failed to add task: ${error.response.data.detail}`);
    }
  }

  return (
    <>
      <DndContext
        id="dnd-context-for-task-list"
        sensors={dndSensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext items={tasks} strategy={verticalListSortingStrategy}>
          <div className="items-center flex-col">
            <div className="xl:px-40">
              <div className="flex items-center justify-between">
                <h1 className="text-xl font-semibold md:text-2xl">
                  {section?.title}
                </h1>
              </div>
              <div className="flex flex-col py-4">
                {tasks.map((task) => (
                  <div key={task.id}>
                    <div>
                      <Task
                        task={task}
                        skeleton={isLoading}
                        handleToggleTaskCompleted={handleToggleTaskCompleted}
                        handleToggleTaskArchived={handleToggleTaskArchived}
                        mutateSection={mutateSection}
                        handleTaskEdit={handleTaskEdit}
                        key={task.id}
                      />
                    </div>
                    <hr className="border-gray-200 dark:border-white" />
                  </div>
                ))}
                <div>
                  <div
                    className="py-3.5 px-2 text-small cursor-pointer"
                    onClick={() => setIsAddTaskDialogOpen(true)}
                  >
                    <div className="flex items-center justify-start w-full">
                      <Plus className="mx-2 w-5 h-5 " />
                      Add task
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </SortableContext>
      </DndContext>

      <AddTaskDialog
        isOpen={isAddTaskDialogOpen}
        onOpenChange={setIsAddTaskDialogOpen}
        handleTaskAdd={handleTaskAdd}
      />
    </>
  );
}
