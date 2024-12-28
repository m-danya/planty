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
import { Task } from "./tasks/task";
import {
  toggleTaskArchived,
  toggleTaskCompleted,
  updateTask,
} from "@/api/api-calls";

function CalendarView() {
  const [isPopoverOpen, setIsPopoverOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const weekStart = startOfWeek(selectedDate, { weekStartsOn: 1 });
  const weekEnd = endOfWeek(selectedDate, { weekStartsOn: 1 });
  const {
    tasksByDate,
    isLoading,
    isError,
    mutate: mutateTasksByDate,
  } = useTasksByDate(weekStart, weekEnd);

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

  function getFormattedDate(date: Date): string {
    const currentYear = new Date().getFullYear();

    const includeYear = date.getFullYear() !== currentYear;
    // TODO: add day of week here
    return format(date, includeYear ? "MMM dd, yyyy, EEEE" : "MMM dd, EEEE", {
      locale: enUS,
    });
  }

  const weekRange = selectedDate ? getWeekRange(selectedDate) : "";

  return (
    <div>
      <div className="flex items-center gap-2 justify-center">
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
      <div className="py-5">
        {tasksByDate &&
          tasksByDate.map((date_with_tasks) => (
            <div
              className="items-center flex-col"
              key={`${date_with_tasks.date}_tasks`}
            >
              <div className="xl:px-20">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-semibold md:text-xl">
                    {getFormattedDate(new Date(date_with_tasks.date))}
                  </h3>
                </div>
                <div className="flex flex-col py-4">
                  {date_with_tasks.tasks.map((task: TaskResponse) => (
                    <div key={task.id}>
                      <div>
                        <Task
                          task={task}
                          skeleton={isLoading}
                          handleToggleTaskCompleted={async (task_id) => {
                            await toggleTaskCompleted(task_id);
                            mutateTasksByDate();
                          }}
                          handleToggleTaskArchived={async (task_id) => {
                            await toggleTaskArchived(task_id);
                            mutateTasksByDate();
                          }}
                          mutateOnTaskMove={mutateTasksByDate}
                          handleTaskEdit={async (updateTaskData) => {
                            await updateTask(updateTaskData);
                            mutateTasksByDate();
                          }}
                          key={task.id}
                        />
                      </div>
                      <hr className="border-gray-200 dark:border-white" />
                    </div>
                  ))}
                  {/* <div>
                      <div
                        className="py-3.5 px-2 text-small cursor-pointer"
                        onClick={() => setIsAddTaskDialogOpen(true)}
                      >
                        <div className="flex items-center justify-start w-full">
                          <Plus className="mx-2 w-5 h-5 " />
                          Add task
                        </div>
                      </div>
                    </div> */}
                </div>
              </div>
            </div>
          ))}
      </div>
    </div>
  );
}

export default CalendarView;
