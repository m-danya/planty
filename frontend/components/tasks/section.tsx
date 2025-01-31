"use client";

import { AddTaskDialog } from "@/components/tasks/add-task-dialog";
import { Task } from "@/components/tasks/task";
import { useSection } from "@/hooks/use-section";
import {
  closestCenter,
  DndContext,
  DragEndEvent,
  MouseSensor,
  TouchSensor,
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
import { TaskResponse, TaskUpdateRequest } from "@/api/Api";

export function Section({ sectionId }: { sectionId: string }) {
  const { section, isLoading, mutate: mutateSection } = useSection(sectionId);

  const tasksFillers = Array.from({ length: 5 }, (_, index) => ({
    id: index.toString(),
    title: "Task " + index,
    description: "Description " + index,
    due_to: "2025-01-01",
    recurrence: null,
    section_id: sectionId,
    content: "Content " + index,
    is_completed: false,
    is_archived: false,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    added_at: new Date().toISOString(),
    attachments: [],
  }));

  const [tasks, setTasks] = useState<TaskResponse[]>(tasksFillers);
  const [isAddTaskDialogOpen, setIsAddTaskDialogOpen] = useState(false);

  useEffect(() => {
    if (section?.tasks) {
      setTasks(section.tasks);
    }
  }, [section]);

  const dndSensors = useSensors(
    useSensor(MouseSensor, {
      activationConstraint: {
        distance: 5,
      },
    }),
    useSensor(TouchSensor, {
      activationConstraint: { distance: 5, delay: 500 },
    })
  );

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
        console.log(error);
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
                {tasks.map((task: TaskResponse) => (
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
                        handleTaskEdit={async (
                          updateTaskData: TaskUpdateRequest
                        ) => {
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
        handleTaskAdd={async (task) => {
          await createTask(sectionId, task);
          mutateSection();
        }}
      />
    </>
  );
}
