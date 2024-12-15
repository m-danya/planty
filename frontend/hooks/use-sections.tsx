import useSWR from "swr";
import { fetcher } from "@/hooks/fetcher";
import { SectionResponse } from "@/api/Api";

export const useSections = ({
  leavesOnly = false,
  asTree = true,
}: { leavesOnly?: boolean; asTree?: boolean } = {}) => {
  const { data, error, isLoading, mutate } = useSWR<SectionResponse[]>(
    `/api/sections?leaves_only=${leavesOnly}&as_tree=${asTree}`,
    fetcher
  );
  let rootSectionId;
  let sections;
  if (asTree) {
    if (leavesOnly) {
      sections = data;
    } else {
      rootSectionId = data?.[0]?.id;
      sections = data?.[0]?.subsections;
    }
  } else {
    sections = data;
    rootSectionId = sections?.find((s) => !s.parent_id)?.id;
  }
  return {
    sections: sections,
    rootSectionId: rootSectionId,
    isLoading,
    isError: error,
    mutate: mutate,
  };
};
