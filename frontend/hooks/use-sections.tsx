import useSWR from "swr";
import { fetcher } from "@/hooks/fetcher";

export const useSections = () => {
  const { data, error, isLoading } = useSWR("/api/sections", fetcher);
  let rootSectionId = data?.[0]?.id;
  return {
    sections: data?.[0]?.subsections,
    rootSectionId: data?.[0].id,
    isLoading,
    isError: error,
  };
};
