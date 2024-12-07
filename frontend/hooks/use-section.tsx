import useSWR from "swr";
import { fetcher } from "@/hooks/fetcher";

export const useSection = (sectionId: string) => {
  let data, error, isLoading, mutate;

  if (sectionId === "archived") {
    ({ data, error, isLoading, mutate } = useSWR(
      "/api/tasks/archived",
      fetcher
    ));
    data = {
      tasks: data,
    };
  } else {
    ({ data, error, isLoading, mutate } = useSWR(
      `/api/section/${sectionId}`,
      fetcher
    ));
  }

  return {
    section: data,
    isLoading,
    isError: error,
    mutate: mutate,
  };
};
