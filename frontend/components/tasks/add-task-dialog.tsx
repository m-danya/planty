"use client";

import React from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { TaskDialogForm } from "./task-dialog-form";

interface AddTaskDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  handleTaskAdd: (task: {
    title: string;
    description: string;
    due_to: string | null;
  }) => void;
}

export function AddTaskDialog({
  isOpen,
  onOpenChange,
  handleTaskAdd,
}: AddTaskDialogProps) {
  const handleCancel = () => {
    onOpenChange(false);
  };

  const handleSubmit = (task: {
    title: string;
    description: string;
    due_to: string | null;
  }) => {
    handleTaskAdd(task);
    onOpenChange(false);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Task</DialogTitle>
        </DialogHeader>
        <TaskDialogForm
          initialTitle=""
          initialDescription=""
          initialDueTo={null}
          submitLabel="Add"
          onSubmit={handleSubmit}
          onCancel={handleCancel}
        />
      </DialogContent>
    </Dialog>
  );
}
