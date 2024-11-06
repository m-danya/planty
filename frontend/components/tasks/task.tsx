"use client";

import { Checkbox } from "@/components/ui/checkbox";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

export function Task({ task, handleToggleTaskCompleted }) {
  const { attributes, listeners, setNodeRef, transform, transition } =
    useSortable({ id: task.id });

  const dndStyle = {
    transform: CSS.Translate.toString(transform),
    transition,
  };

  return (
    <div
      ref={setNodeRef}
      style={dndStyle}
      {...attributes}
      {...listeners}
      key={task.id}
    >
      <div className="py-3.5 px-2 text-small">
        <div className="flex items-center justify-start w-full">
          <Checkbox
            className="mx-2 w-5 h-5 rounded-xl"
            checked={task.isCompleted}
            onCheckedChange={(e) =>
              handleToggleTaskCompleted({
                ...task,
                isCompleted: e,
              })
            }
          />
          <div className="flex flex-col items-center">{task.title}</div>
        </div>
        {task.description && (
          <div className="ml-9 text-gray-400 pt-0.5">{task.description}</div>
        )}
      </div>
    </div>
  );
}
