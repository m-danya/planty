import useSWR from "swr";
import { fetcher } from "@/hooks/fetcher";
import { SectionResponse } from "@/api/Api";

export const useSections = ({
  leavesOnly = false,
}: { leavesOnly?: boolean } = {}) => {
  const { data, error, isLoading } = useSWR<SectionResponse[]>(
    `/api/sections?leaves_only=${leavesOnly}`,
    fetcher
  );
  let rootSectionId;
  let sections;
  if (leavesOnly) {
    sections = data;
  } else {
    rootSectionId = data?.[0]?.id;
    sections = data?.[0]?.subsections;
  }
  return {
    sections: sections,
    rootSectionId: rootSectionId,
    isLoading,
    isError: error,
  };
};
