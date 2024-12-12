"use client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { format } from "date-fns";
import { TaskDialogForm } from "./task-dialog-form";
import React, { useRef } from "react";

interface EditTaskDialogProps {
  isEditing: boolean;
  onOpenChange: (open: boolean) => void;
  task: {
    id: string;
    title: string;
    description?: string | null;
    due_to?: string | null;
  };
  handleTaskEdit: (task: any) => void;
}

export function EditTaskDialog({
  isEditing,
  onOpenChange,
  task,
  handleTaskEdit,
}: EditTaskDialogProps) {
  const initialTitle = task.title || "";
  const initialDescription = task.description || "";
  const initialDueTo = task.due_to ? new Date(task.due_to) : null;

  const titleInputRef = useRef<HTMLInputElement>(null);

  const handleCancel = () => {
    onOpenChange(false);
  };

  const handleSubmit = (updatedTask: {
    title: string;
    description: string;
    due_to: string | null;
  }) => {
    handleTaskEdit({
      id: task.id,
      title: updatedTask.title,
      description: updatedTask.description,
      due_to: updatedTask.due_to
        ? format(new Date(updatedTask.due_to), "yyyy-MM-dd")
        : null,
    });
    onOpenChange(false);
  };

  return (
    <Dialog open={isEditing} onOpenChange={onOpenChange}>
      <DialogContent
        onOpenAutoFocus={(event) => {
          // prevent selecting the title
          event.preventDefault();
          if (titleInputRef.current) {
            // focus on title (without selecting)
            titleInputRef.current.focus();
          }
        }}
      >
        <DialogHeader>
          <DialogTitle>Edit Task</DialogTitle>
        </DialogHeader>
        <TaskDialogForm
          initialTitle={initialTitle}
          initialDescription={initialDescription}
          initialDueTo={initialDueTo}
          submitLabel="Save"
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          titleInputRef={titleInputRef}
        />
      </DialogContent>
    </Dialog>
  );
}
