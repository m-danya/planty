"use client";

import React, { useState, forwardRef } from "react";
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
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";
import { X } from "lucide-react";
import { DateLabel } from "./date-label";
import { format } from "date-fns";
import { RecurrenceInfo } from "@/api/Api";

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

    const handleDateSelect = (date: Date) => {
      setDueTo(date);
      setIsPopoverOpen(false);
    };

    const clearDate = () => setDueTo(null);

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

          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="recurrence_toggle"
                checked={isRecurring}
                onCheckedChange={(checked) => setIsRecurring(!!checked)}
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
                  <Label htmlFor="recurrence_flexible">Flexible mode</Label>
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
