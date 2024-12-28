"use client";

import { RecurrenceInfo } from "@/api/Api";
import { AddTaskDialog } from "@/components/tasks/add-task-dialog";
import { Task } from "@/components/tasks/task";
import { useSection } from "@/hooks/use-section";
import {
  closestCenter,
  DndContext,
  DragEndEvent,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { Plus } from "lucide-react";
import { useEffect, useState } from "react";

import {
  createTask,
  moveTask,
  toggleTaskArchived,
  toggleTaskCompleted,
  updateTask,
} from "@/api/api-calls";

export function Section({ sectionId }: { sectionId: string }) {
  const {
    section,
    isLoading,
    isError,
    mutate: mutateSection,
  } = useSection(sectionId);

  const tasksFillers = Array.from({ length: 5 }, (_, index) => ({
    id: index.toString(),
  }));

  const [tasks, setTasks] = useState(tasksFillers);
  const [isAddTaskDialogOpen, setIsAddTaskDialogOpen] = useState(false);

  useEffect(() => {
    if (section?.tasks) {
      setTasks(section.tasks);
    }
  }, [section]);

  const dndSensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 1 } })
  );

  async function handleToggleTaskArchived(task_id: string) {
    await toggleTaskArchived(task_id);
    mutateSection();
  }

  async function handleTaskAdd(task: {
    title: string;
    description: string;
    due_to: string | null;
    recurrence: RecurrenceInfo | null;
  }) {
    try {
      await createTask(sectionId, task);
      mutateSection();
    } catch (error: any) {
      alert(
        `Failed to add task: ${error.response?.data?.detail || error.message}`
      );
    }
  }

  async function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (!over) return;

    const oldIndex = tasks.findIndex((task) => task.id === active.id);
    const newIndex = tasks.findIndex((task) => task.id === over.id);

    if (active.id !== over.id) {
      setTasks((tasks) => arrayMove(tasks, oldIndex, newIndex));

      try {
        await moveTask(active.id as string, sectionId, newIndex);
      } catch (error) {
        alert("Failed to move task");
        // revert changes in UI
        setTasks((tasks) => arrayMove(tasks, newIndex, oldIndex));
      }
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
                        handleToggleTaskCompleted={async (task_id) => {
                          await toggleTaskCompleted(task_id);
                          mutateSection();
                        }}
                        handleToggleTaskArchived={async (task_id) => {
                          await toggleTaskArchived(task_id);
                          mutateSection();
                        }}
                        mutateOnTaskMove={mutateSection}
                        handleTaskEdit={async (updateTaskData) => {
                          await updateTask(updateTaskData);
                          mutateSection();
                        }}
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
