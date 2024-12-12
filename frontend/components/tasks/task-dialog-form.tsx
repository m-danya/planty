"use client";

import React, { useState, useEffect, forwardRef } from "react";
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
import { DateLabel } from "./date-label";
import { format } from "date-fns";

interface TaskDialogFormProps {
  initialTitle?: string;
  initialDescription?: string;
  initialDueTo?: Date | null;
  submitLabel: string;
  onSubmit: (task: {
    title: string;
    description: string;
    due_to: string | null;
  }) => void;
  onCancel: () => void;
  titleInputRef?: React.RefObject<HTMLInputElement>;
}

export const TaskDialogForm = forwardRef<HTMLInputElement, TaskDialogFormProps>(
  (
    {
      initialTitle = "",
      initialDescription = "",
      initialDueTo = null,
      submitLabel,
      onSubmit,
      onCancel,
      titleInputRef,
    },
    ref
  ) => {
    const [title, setTitle] = useState(initialTitle);
    const [description, setDescription] = useState(initialDescription);
    const [dueTo, setDueTo] = useState<Date | null>(initialDueTo);
    const [isPopoverOpen, setIsPopoverOpen] = useState(false);

    const handleFinish = (e: React.FormEvent) => {
      e.preventDefault();
      onSubmit({
        title,
        description,
        due_to: dueTo ? format(dueTo, "yyyy-MM-dd") : null,
      });
    };

    const handleDateSelect = (date: Date) => {
      setDueTo(date);
      setIsPopoverOpen(false);
    };

    const clearDate = () => setDueTo(null);

    return (
      <div>
        <form onSubmit={handleFinish} className="space-y-4 mt-4">
          <div>
            <Label htmlFor="title">Title</Label>
            <Input
              id="title"
              ref={titleInputRef}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>
          <div>
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
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
                    {dueTo ? (
                      <DateLabel date={dueTo} isRecurrent={false} />
                    ) : (
                      <span>Pick a date</span>
                    )}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    weekStartsOn={1}
                    selected={dueTo}
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
            <Button variant="outline" onClick={onCancel} type="button">
              Cancel
            </Button>
            <Button type="submit">{submitLabel}</Button>
          </div>
        </form>
      </div>
    );
  }
);

TaskDialogForm.displayName = "TaskDialogForm"; // for devtools
