"use client";

import React, { useState } from "react";
import { Checkbox } from "@/components/ui/checkbox";
import { TaskResponse } from "@/api/Api";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { DateLabel } from "./date-label";
import { EditTaskDialog } from "./edit-task-dialog";
import { MoveTaskDialog } from "./move-task-dialog";
import { TaskContextMenu } from "./task-context-menu";
import { parseISO } from "date-fns";

interface TaskProps {
  task: TaskResponse;
  handleToggleTaskCompleted: (taskId: string) => void;
  skeleton?: boolean;
  mutateSection: () => void;
  handleTaskEdit: (task: any) => void;
}

export function Task({
  task,
  handleToggleTaskCompleted,
  skeleton = false,
  mutateSection,
  handleTaskEdit,
}: TaskProps) {
  const [moveTaskDialogIsOpen, setMoveTaskDialogIsOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [isContextMenuOpen, setIsContextMenuOpen] = useState(false);
  const isDragDisabled = moveTaskDialogIsOpen || isEditing || isContextMenuOpen;

  const { attributes, listeners, setNodeRef, transform, transition } =
    useSortable({ id: task.id, disabled: isDragDisabled });

  const dndStyle = {
    transform: CSS.Translate.toString(transform),
    transition,
  };

  const taskDueTo = task.due_to && parseISO(task.due_to);

  return (
    <div ref={setNodeRef} style={dndStyle} {...attributes} {...listeners}>
      <TaskContextMenu
        onOpenMoveDialog={() => setMoveTaskDialogIsOpen(true)}
        onContextMenuChange={setIsContextMenuOpen}
      >
        <div
          className="py-3.5 px-2 text-small cursor-pointer"
          onClick={() => {
            setIsEditing(true);
          }}
        >
          <div className="flex items-center justify-start w-full">
            {skeleton && (
              <div className="mx-2 rounded-full bg-gray-100 h-5 w-5"></div>
            )}
            {!skeleton && (
              <Checkbox
                className="mx-2 w-5 h-5 rounded-xl"
                checked={task.is_completed}
                onClick={(e) => e.stopPropagation()}
                onCheckedChange={() => handleToggleTaskCompleted(task.id)}
              />
            )}
            {skeleton && (
              <div className="h-4 flex-none w-32 bg-gray-100 rounded"></div>
            )}
            {!skeleton && (
              <div className="flex flex-col items-start">
                <div>{task.title}</div>
                {task.due_to && <DateLabel date={taskDueTo} />}
              </div>
            )}
          </div>
          {!skeleton && task.description && (
            <div className="ml-9 text-gray-400 pt-0.5">{task.description}</div>
          )}
        </div>
      </TaskContextMenu>

      <MoveTaskDialog
        open={moveTaskDialogIsOpen}
        onOpenChange={setMoveTaskDialogIsOpen}
        taskTitle={task.title}
        taskId={task.id}
        mutateSection={mutateSection}
      />

      <EditTaskDialog
        isEditing={isEditing}
        onOpenChange={setIsEditing}
        task={task}
        handleTaskEdit={handleTaskEdit}
      />
    </div>
  );
}
