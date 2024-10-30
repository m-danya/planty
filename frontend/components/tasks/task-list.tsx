"use client";

import { Task } from "@/components/tasks/task";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { useState } from "react";

const exampleTasks = [
  { id: 1, name: "Watch 'BoJack Horseman'", isCompleted: true },
  {
    id: 2,
    name: "Task with description",
    description: "some description here",
    isCompleted: true,
  },
  { id: 3, name: "Clean the house" },
  { id: 4, name: "Some completed archived task" },
  { id: 5, name: "Go to the gym", description: "💪🏻💪🏻💪🏻" },
  { id: 6, name: "A task with date", date: "2024-12-28" },
];

export function TaskList() {
  const [tasks, setTasks] = useState(exampleTasks);
  const dndSensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 1 } }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  function handleToggleTaskCompleted(new_task) {
    setTasks((tasks) =>
      tasks.map((task) => {
        if (task.id === new_task.id) {
          return new_task;
        } else {
          return task;
        }
      })
    );
  }

  function handleDragEnd(event) {
    const { active, over } = event;

    if (active.id !== over.id) {
      setTasks((tasks) => {
        const oldIndex = tasks.findIndex((task) => task.id === active.id);
        const newIndex = tasks.findIndex((task) => task.id === over.id);

        return arrayMove(tasks, oldIndex, newIndex);
      });
    }
  }

  return (
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
              <h1 className="text-xl font-semibold md:text-2xl">Tasks</h1>
            </div>
            <div className="flex flex-col py-4">
              {tasks.map((task) => (
                <div key={task.id}>
                  <div>
                    <Task
                      task={task}
                      handleToggleTaskCompleted={handleToggleTaskCompleted}
                    />
                  </div>
                  <hr className="border-gray-200 dark:border-white" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </SortableContext>
    </DndContext>
  );
}
