"use client";

import { Checkbox } from "@/components/ui/checkbox";
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
} from "@/components/ui/context-menu";
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
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { MoveRight, X } from "lucide-react";
import { useState } from "react";
import { MoveTaskToSectionForm } from "./move-task-to-section-form";

export function Task({
  task,
  handleToggleTaskCompleted,
  skeleton,
  mutateSection,
  handleTaskEdit,
}) {
  const { attributes, listeners, setNodeRef, transform, transition } =
    useSortable({ id: task.id });

  const [moveTaskDialogIsOpen, setMoveTaskDialogIsOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedTitle, setEditedTitle] = useState(task.title);
  const [editedDescription, setEditedDescription] = useState(task.description);

  const dndStyle = {
    transform: CSS.Translate.toString(transform),
    transition,
  };

  const handleFinishChangingTask = () => {
    handleTaskEdit({
      id: task.id,
      title: editedTitle,
      description: editedDescription,
    });
    setIsEditing(false);
  };

  return (
    <div
      ref={setNodeRef}
      style={dndStyle}
      {...attributes}
      {...listeners}
      key={task.id}
    >
      <ContextMenu key={`${task.id}_context_menu`}>
        <ContextMenuTrigger>
          <div
            className="py-3.5 px-2 text-small"
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
                  checked={task.isCompleted}
                  onCheckedChange={(e) =>
                    handleToggleTaskCompleted({
                      ...task,
                      isCompleted: e,
                    })
                  }
                />
              )}
              {skeleton && (
                <div className="h-4 flex-none w-32 bg-gray-100 rounded"></div>
              )}
              {!skeleton && (
                <div className="flex flex-col items-center">{task.title}</div>
              )}
            </div>
            {!skeleton && task.description && (
              <div className="ml-9 text-gray-400 pt-0.5">
                {task.description}
              </div>
            )}
          </div>
        </ContextMenuTrigger>
        <ContextMenuContent>
          <ContextMenuItem>
            <div
              className="flex items-center gap-x-2"
              onClick={() => {
                setMoveTaskDialogIsOpen(true);
              }}
            >
              <MoveRight />
              Move to another section
            </div>
          </ContextMenuItem>
          <ContextMenuItem>
            <div className="flex items-center gap-x-2">
              <X />
              Remove
            </div>
          </ContextMenuItem>
        </ContextMenuContent>
      </ContextMenu>

      {/* Move Task Dialog */}
      <Dialog
        open={moveTaskDialogIsOpen}
        onOpenChange={setMoveTaskDialogIsOpen}
        key={`${task.id}_section_dialog`}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Move "{task.title}" to another section</DialogTitle>
          </DialogHeader>

          <MoveTaskToSectionForm
            taskId={task.id}
            afterSubmit={() => {
              mutateSection();
              setMoveTaskDialogIsOpen(false);
            }}
          />
        </DialogContent>
      </Dialog>

      {/* Edit Task Dialog */}
      <Dialog
        open={isEditing}
        onOpenChange={setIsEditing}
        key={`${task.id}_edit_dialog`}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Task</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                value={editedTitle}
                onChange={(e) => setEditedTitle(e.target.value)}
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
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setIsEditing(false)}>
                Cancel
              </Button>
              <Button onClick={handleFinishChangingTask}>Save</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
