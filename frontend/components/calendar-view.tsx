"use client";

import { TaskResponse } from "@/api/Api";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { useTasksByDate } from "@/hooks/use-tasks-by-date";
import { endOfWeek, format, startOfWeek } from "date-fns";
import { enUS } from "date-fns/locale";
import { useState } from "react";

function CalendarView() {
  const [isPopoverOpen, setIsPopoverOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const weekStart = startOfWeek(selectedDate, { weekStartsOn: 1 });
  const weekEnd = endOfWeek(selectedDate, { weekStartsOn: 1 });
  const { tasksByDate, isLoading, isError, mutate } = useTasksByDate(
    weekStart,
    weekEnd
  );

  const handleDateSelect = (date: Date) => {
    setSelectedDate(date);
    setIsPopoverOpen(false);
  };

  function getWeekRange(date: Date): string {
    const currentYear = new Date().getFullYear();

    const includeYear =
      weekStart.getFullYear() !== currentYear ||
      weekEnd.getFullYear() !== currentYear;

    const formattedStart = format(
      weekStart,
      includeYear ? "MMM dd, yyyy" : "MMM dd",
      { locale: enUS }
    );
    const formattedEnd = format(
      weekEnd,
      includeYear ? "MMM dd, yyyy" : "MMM dd",
      { locale: enUS }
    );

    return `${formattedStart} — ${formattedEnd}`;
  }

  const weekRange = selectedDate ? getWeekRange(selectedDate) : "";

  return (
    <div>
      <div className="flex items-center gap-2">
        <div>
          <Popover open={isPopoverOpen} onOpenChange={setIsPopoverOpen}>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className="w-full justify-start text-left font-normal"
              >
                {selectedDate ? (
                  <div>{weekRange}</div>
                ) : (
                  <span>Pick a date</span>
                )}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0">
              <Calendar
                mode="single"
                weekStartsOn={1}
                selected={selectedDate}
                onSelect={handleDateSelect}
                defaultMonth={selectedDate}
                required
              />
            </PopoverContent>
          </Popover>
        </div>
      </div>
      <div>
        {tasksByDate &&
          Object.keys(tasksByDate).map((date) => (
            <div key={date}>
              <h1>{date}</h1>
              {tasksByDate[date].map((task: TaskResponse) => (
                <div>{task.title}</div>
              ))}
            </div>
          ))}
      </div>
    </div>
  );
}

export default CalendarView;
