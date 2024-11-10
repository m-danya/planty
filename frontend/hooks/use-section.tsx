import useSWR from "swr";
import { fetcher } from "@/hooks/fetcher";

export const useSection = (sectionId) => {
  const { data, error, isLoading, mutate } = useSWR(
    `/api/section/${sectionId}`,
    fetcher
  );
  return {
    section: data,
    isLoading,
    isError: error,
    mutate: mutate,
  };
};
