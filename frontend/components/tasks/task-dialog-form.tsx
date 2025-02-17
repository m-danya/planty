"use client";

import { RecurrenceInfo } from "@/api/Api";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { format } from "date-fns";
import { X } from "lucide-react";
import React, { forwardRef, useState } from "react";
import { DateLabel } from "./date-label";

interface TaskDialogFormProps {
  initialTitle?: string;
  initialDescription?: string;
  initialDueTo?: Date | null;
  initialRecurrence?: RecurrenceInfo | null;
  submitLabel: string;
  onSubmit: (task: {
    title: string;
    description: string;
    due_to: string | null;
    recurrence: RecurrenceInfo | null;
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
      initialRecurrence = null,
      submitLabel,
      onSubmit,
      onCancel,
      titleInputRef,
    },
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    ref
  ) => {
    const [title, setTitle] = useState(initialTitle);
    const [description, setDescription] = useState(initialDescription);
    const [dueTo, setDueTo] = useState<Date | null>(initialDueTo);
    const [isPopoverOpen, setIsPopoverOpen] = useState(false);

    const [isRecurring, setIsRecurring] = useState<boolean>(
      Boolean(initialRecurrence)
    );
    const [period, setPeriod] = useState<number>(
      initialRecurrence?.period ?? 3
    );
    const [recurrenceType, setRecurrenceType] = useState<
      "days" | "weeks" | "months" | "years"
    >(initialRecurrence?.type ?? "days");
    const [flexibleMode, setFlexibleMode] = useState<boolean>(
      initialRecurrence?.flexible_mode ?? false
    );

    const handleFinish = (e: React.FormEvent) => {
      e.preventDefault();

      const recurrenceObject: RecurrenceInfo | null = isRecurring
        ? {
            period,
            type: recurrenceType,
            flexible_mode: flexibleMode,
          }
        : null;

      onSubmit({
        title,
        description,
        due_to: dueTo ? format(dueTo, "yyyy-MM-dd") : null,
        recurrence: recurrenceObject,
      });
    };

    const handleDateSelect = (date: Date | undefined) => {
      if (date) {
        setDueTo(date);
        setIsPopoverOpen(false);
      }
    };

    const clearDate = () => {
      setIsRecurring(false);
      setDueTo(null);
    };

    return (
      <div>
        <form
          onSubmit={handleFinish}
          className="space-y-4 mt-4"
          autoComplete="off"
        >
          <div>
            <Label htmlFor="task_title">Title</Label>
            <Input
              id="task_title"
              ref={titleInputRef}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>
          <div>
            <Label htmlFor="task_description">Description</Label>
            <Textarea
              id="task_description"
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
                    variant="outline"
                    className="w-full justify-start text-left font-normal"
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
                    selected={dueTo ?? undefined}
                    onSelect={handleDateSelect}
                    defaultMonth={dueTo ?? undefined}
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

          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="recurrence_toggle"
                checked={isRecurring}
                onCheckedChange={(checked) => setIsRecurring(!!checked)}
                disabled={!dueTo}
              />
              <Label htmlFor="recurrence_toggle">
                This task is recurring {isRecurring ? "every" : ""}
              </Label>
            </div>
            {isRecurring && (
              <div className="grid grid-cols-1 gap-2 md:grid-cols-3 md:gap-4">
                <div>
                  {/* <Label htmlFor="recurrence_period">Period</Label> */}
                  <Input
                    id="recurrence_period"
                    type="number"
                    value={period}
                    onChange={(e) => setPeriod(Number(e.target.value))}
                  />
                </div>
                <div>
                  {/* <Label htmlFor="recurrence_type">Period type</Label> */}
                  <Select
                    value={recurrenceType}
                    onValueChange={(value) =>
                      setRecurrenceType(
                        value as "days" | "weeks" | "months" | "years"
                      )
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="days">days</SelectItem>
                      <SelectItem value="weeks">weeks</SelectItem>
                      <SelectItem value="months">months</SelectItem>
                      <SelectItem value="years">years</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="recurrence_flexible"
                    checked={flexibleMode}
                    onCheckedChange={(checked) => setFlexibleMode(!!checked)}
                  />
                  <Label htmlFor="recurrence_flexible">
                    Flexible mode
                    <span
                      className="mx-2 text-muted-foreground cursor-pointer"
                      title="Flexible mode adjusts a task's recurrence based on the completion date instead of the original due date. For example, let's set a task recurring every 7 days with flexible mode enabled. Completing it on December 22 sets the next due date to December 29. Completing it later, on December 24, shifts the next due date to December 31."
                    >
                      ?
                    </span>
                  </Label>
                </div>
              </div>
            )}
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
