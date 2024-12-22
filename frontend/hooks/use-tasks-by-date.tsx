import useSWR from "swr";
import { fetcher } from "@/hooks/fetcher";
import { format } from "date-fns";

export const useTasksByDate = (date_from: Date, date_to: Date) => {
  const query = new URLSearchParams({
    not_before: format(date_from, "yyyy-MM-dd"),
    not_after: format(date_to, "yyyy-MM-dd"),
  });

  const { data, error, isLoading, mutate } = useSWR(
    `/api/task/by_date?${query.toString()}`,
    fetcher
  );

  return {
    tasksByDate: data,
    isLoading,
    isError: error,
    mutate,
  };
};
