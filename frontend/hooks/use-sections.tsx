import useSWR from "swr";
import { fetcher } from "@/hooks/fetcher";

export const useSections = ({ asTree = true }: { asTree?: boolean } = {}) => {
  const { data, error, isLoading } = useSWR(
    `/api/sections?as_tree=${asTree}`,
    fetcher
  );
  let rootSectionId;
  let sections;
  if (asTree) {
    rootSectionId = data?.[0]?.id;
    sections = data?.[0]?.subsections;
  } else {
    sections = data;
  }
  return {
    sections: sections,
    rootSectionId: rootSectionId,
    isLoading,
    isError: error,
  };
};
