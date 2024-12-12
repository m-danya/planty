"use client";

import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Popover,
  PopoverTrigger,
  PopoverContent,
} from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";
import { X } from "lucide-react";
import { format } from "date-fns";
import { DateLabel } from "./date-label";

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
  const [editedTitle, setEditedTitle] = useState(task.title);
  const [editedDescription, setEditedDescription] = useState(
    task.description || ""
  );
  const [editedDueTo, setEditedDueTo] = useState<Date | null>(
    task.due_to ? new Date(task.due_to) : null
  );
  const [isPopoverOpen, setIsPopoverOpen] = useState(false);

  const handleFinishChangingTask = (e: React.FormEvent) => {
    e.preventDefault();
    handleTaskEdit({
      id: task.id,
      title: editedTitle,
      description: editedDescription,
      due_to: editedDueTo ? format(editedDueTo, "yyyy-MM-dd") : null,
    });
    onOpenChange(false);
  };

  const handleDateSelect = (date: Date) => {
    setEditedDueTo(date);
    setIsPopoverOpen(false);
  };

  const clearDate = () => setEditedDueTo(null);

  const resetEditedValues = () => {
    setEditedTitle(task.title);
    setEditedDescription(task.description || "");
    setEditedDueTo(task.due_to ? new Date(task.due_to) : null);
  };

  useEffect(() => {
    if (isEditing) {
      resetEditedValues();
    }
  }, [isEditing]);

  return (
    <Dialog open={isEditing} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit Task</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleFinishChangingTask}>
          <div className="space-y-4">
            <div>
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                value={editedTitle}
                onChange={(e) => setEditedTitle(e.target.value)}
                required
              />
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={editedDescription}
                onChange={(e) => setEditedDescription(e.target.value)}
              />
            </div>
            <div>
              <Label>Due Date</Label>
              <div className="flex items-center gap-2">
                <Popover open={isPopoverOpen} onOpenChange={setIsPopoverOpen}>
                  <PopoverTrigger asChild>
                    <Button
                      variant={"outline"}
                      className={"w-full justify-start text-left font-normal"}
                    >
                      {editedDueTo ? (
                        <DateLabel date={editedDueTo} />
                      ) : (
                        <span>Pick a date</span>
                      )}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar
                      mode="single"
                      weekStartsOn={1}
                      selected={editedDueTo}
                      onSelect={handleDateSelect}
                      required
                    />
                  </PopoverContent>
                </Popover>
                <Button
                  variant="ghost"
                  size="icon"
                  type="button"
                  onClick={clearDate}
                  aria-label="Clear Date"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <div className="flex justify-end space-x-2">
              <Button
                variant="outline"
                onClick={() => onOpenChange(false)}
                type="button"
              >
                Cancel
              </Button>
              <Button type="submit">Save</Button>
            </div>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
