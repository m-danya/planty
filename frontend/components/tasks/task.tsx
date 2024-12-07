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
import { MoveRight, X, CalendarIcon, Archive } from "lucide-react";
import { useState, useEffect } from "react";
import { MoveTaskToSectionForm } from "./move-task-to-section-form";
import {
  Popover,
  PopoverTrigger,
  PopoverContent,
} from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";

import {
  format,
  isToday,
  isYesterday,
  isTomorrow,
  isThisWeek,
  isSameYear,
  parseISO,
  startOfDay,
  isAfter,
} from "date-fns";
import { TaskResponse } from "@/api/Api";

export function Task({
  task,
  handleToggleTaskCompleted,
  skeleton = false,
  mutateSection,
  handleTaskEdit,
}: {
  task: TaskResponse;
  handleToggleTaskCompleted: (taskId: string) => void;
  skeleton?: boolean;
  mutateSection: () => void;
  handleTaskEdit: (task: any) => void;
}) {
  const [moveTaskDialogIsOpen, setMoveTaskDialogIsOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedTitle, setEditedTitle] = useState(task.title);
  const [editedDescription, setEditedDescription] = useState(
    task.description || ""
  );
  const [editedDueTo, setEditedDueTo] = useState<Date | null>(
    task.due_to ? new Date(task.due_to) : null
  );
  const [isPopoverOpen, setIsPopoverOpen] = useState(false);
  const [isContextMenuOpen, setIsContextMenuOpen] = useState(false);
  const isDragDisabled = moveTaskDialogIsOpen || isEditing || isContextMenuOpen;

  const { attributes, listeners, setNodeRef, transform, transition } =
    useSortable({ id: task.id, disabled: isDragDisabled });

  const clearDate = () => setEditedDueTo(null);

  const dndStyle = {
    transform: CSS.Translate.toString(transform),
    transition,
  };

  const handleFinishChangingTask = (e: React.FormEvent) => {
    e.preventDefault();
    handleTaskEdit({
      id: task.id,
      title: editedTitle,
      description: editedDescription,
      due_to: editedDueTo ? format(editedDueTo, "yyyy-MM-dd") : null,
    });
    setIsEditing(false);
  };

  const handleDateSelect = (date: Date) => {
    setEditedDueTo(date);
    setIsPopoverOpen(false);
  };

  const taskDueTo = task.due_to && parseISO(task.due_to);

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
    <div
      ref={setNodeRef}
      style={dndStyle}
      {...attributes}
      {...listeners}
      key={task.id}
    >
      <ContextMenu
        onOpenChange={setIsContextMenuOpen}
        key={`${task.id}_context_menu`}
      >
        <ContextMenuTrigger>
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
                  onCheckedChange={(e) => handleToggleTaskCompleted(task.id)}
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
              <div className="ml-9 text-gray-400 pt-0.5">
                {task.description}
              </div>
            )}
          </div>
        </ContextMenuTrigger>
        <ContextMenuContent>
          <ContextMenuItem>
            <div
              className="flex items-center gap-x-2.5 cursor-pointer"
              onClick={() => {
                setMoveTaskDialogIsOpen(true);
              }}
            >
              <MoveRight size={16} />
              Move to another section
            </div>
          </ContextMenuItem>
          <ContextMenuItem>
            <div className="flex items-center gap-x-2.5 cursor-pointer">
              <Archive size={16} />
              Archive
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
                  onClick={() => setIsEditing(false)}
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
    </div>
  );
}

function DateLabel({ date: dateToShow }: { date: Date }) {
  function getDateColorClass(dueDate: Date) {
    const now = new Date();
    if (isAfter(startOfDay(now), startOfDay(dueDate))) {
      return "text-red-600";
    }
    if (isToday(dueDate)) {
      return "text-green-600";
    }
    if (isThisWeek(dueDate, { weekStartsOn: 1 })) {
      return "text-purple-800";
    }
    return "text-gray-600";
  }

  function getFormattedDate(dueDate: Date) {
    const now = new Date();

    if (isToday(dueDate)) {
      return "Today";
    }
    if (isYesterday(dueDate)) {
      return "Yesterday";
    }
    if (isTomorrow(dueDate)) {
      return "Tomorrow";
    }
    if (
      isThisWeek(dueDate, { weekStartsOn: 1 }) &&
      isAfter(startOfDay(dueDate), startOfDay(now))
    ) {
      return format(dueDate, "EEEE"); // Day of the week (e.g., Monday)
    }
    if (isSameYear(dueDate, now)) {
      return format(dueDate, "MMM d"); // Month and day (e.g., Nov 11)
    }
    return format(dueDate, "MMM d, yyyy"); // Month, day, and year (e.g., Nov 11, 2024)
  }

  const colorClass = getDateColorClass(dateToShow);

  return (
    <div className={`my-0.5 text-sm flex items-center ${colorClass}`}>
      <CalendarIcon className={`mr-1 h-4 w-4 ${colorClass}`} />
      {getFormattedDate(dateToShow)}
    </div>
  );
}
