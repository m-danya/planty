"use client";

import { Calendar, CalendarSync } from "lucide-react";
import {
  format,
  isToday,
  isYesterday,
  isTomorrow,
  isThisWeek,
  isSameYear,
  startOfDay,
  isAfter,
} from "date-fns";
import React from "react";

interface DateLabelProps {
  date: Date;
  isRecurrent: boolean;
}

export function DateLabel({ date: dateToShow, isRecurrent }: DateLabelProps) {
  function getDateColorClass(dueDate: Date) {
    const now = new Date();
    if (isAfter(startOfDay(now), startOfDay(dueDate))) {
      return "text-red-600";
    }
    if (isToday(dueDate)) {
      return "text-green-600";
    }
    if (isTomorrow(dueDate)) {
      return "text-orange-800";
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
      {!isRecurrent && <Calendar className={`mr-1 h-4 w-4 ${colorClass}`} />}
      {isRecurrent && <CalendarSync className={`mr-1 h-4 w-4 ${colorClass}`} />}
      {getFormattedDate(dateToShow)}
    </div>
  );
}
