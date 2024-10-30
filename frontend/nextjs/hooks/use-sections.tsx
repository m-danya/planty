import useSWR from "swr";
import { fetcher } from "@/hooks/fetcher";

export const useSections = () => {
  const { data, error, isLoading } = useSWR("/api/sections", fetcher);

  return {
    sections: data,
    isLoading,
    isError: error,
  };
};
