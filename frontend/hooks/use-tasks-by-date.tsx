import useSWR from "swr";
import { fetcher } from "@/hooks/fetcher";
import { format } from "date-fns";
import { TasksByDatesResponse } from "@/api/Api";

export const useTasksByDate = (
  date_from: Date,
  date_to: Date,
  with_overdue: boolean
) => {
  const query = new URLSearchParams({
    not_before: format(date_from, "yyyy-MM-dd"),
    not_after: format(date_to, "yyyy-MM-dd"),
    with_overdue: with_overdue.toString(),
  });

  const { data, error, isLoading, mutate } = useSWR<TasksByDatesResponse>(
    `/api/task/by_date?${query.toString()}`,
    fetcher
  );

  return {
    tasksByDate: data?.by_dates,
    overdueTasks: data?.overdue,
    isLoading,
    isError: error,
    mutate,
  };
};
