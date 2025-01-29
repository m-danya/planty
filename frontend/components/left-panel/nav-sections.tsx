"use client";

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
} from "@/components/ui/context-menu";
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
} from "@/components/ui/sidebar";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowDownUp, ChevronRight, Pencil, Plus, Trash } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/button";

import { useSections } from "@/hooks/use-sections";
import { EditSectionDialog } from "./edit-section-dialog";
import { Api, SectionResponse } from "@/api/Api";
import { useSWRConfig } from "swr";
import { MoveSectionDialog } from "./move-section-dialog";
import { CreateSectionDialog } from "./create-section-dialog";

export function NavSections() {
  const {
    sections,
    rootSectionId,
    isLoading,
    isError,
    mutate: mutateSections,
  } = useSections();
  const [editingSectionId, setEditingSectionId] = useState<string | null>(null);
  const [movingSectionId, setMovingSectionId] = useState<string | null>(null);
  const { cache, mutate } = useSWRConfig();
  const [creatingSection, setCreatingSection] = useState(false);

  if (isError) return <p>Failed to load sections.</p>;

  const api = new Api().api;

  // TODO: move to utils
  function mutateSWRByPartialKey(partialKey: string) {
    Array.from(cache.keys())
      .filter((key: string) => key.includes(partialKey))
      .forEach((key: string) => mutate(key));
  }

  async function handleSectionEdit(updateSectionData: {
    id: string;
    title?: string;
    description?: string;
  }) {
    try {
      const result = await api.patchSectionApiSectionPatch({
        id: updateSectionData.id,
        title: updateSectionData.title,
      });
      console.log("Section edited successfully:", result);
    } catch (error) {
      console.error("Failed to edit section:", error);
      alert("Error while editing section");
    }
    mutateSections();
    // mutate(`/api/section/${updateSectionData.id}`);
    mutateSWRByPartialKey("/api/section/");
  }

  async function handleSectionMove(updateSectionData: {
    parentId: string;
    index: number;
  }) {
    try {
      if (!movingSectionId) {
        throw new Error("Moving section ID is required");
      }
      const result = await api.moveSectionApiSectionMovePost({
        section_id: movingSectionId,
        to_parent_id: updateSectionData.parentId,
        index: updateSectionData.index,
      });
      console.log("Section moved successfully:", result);
    } catch (error: unknown) {
      console.error("Failed to move section:", error);
      alert(
        `Error while moving section: ${
          (error as { response?: { data?: { detail?: string } } })?.response
            ?.data?.detail || "Unknown error"
        }`
      );
    }
    mutateSections();
  }

  async function handleSectionCreate(sectionData: { title: string }) {
    try {
      if (!rootSectionId) {
        throw new Error("Root section ID is required");
      }
      const result = await api.createSectionApiSectionPost({
        title: sectionData.title,
        parent_id: rootSectionId,
      });
      console.log("Section created successfully:", result);
    } catch (error) {
      console.error("Failed to create section:", error);
      alert("Error while creating section");
    }
    mutateSections();
    mutateSWRByPartialKey("/api/section/");
  }

  return (
    <>
      <SidebarGroup className="group-data-[collapsible=icon]:hidden text-nowrap">
        <SidebarGroupLabel>Sections</SidebarGroupLabel>
        <SidebarMenu>
          {isLoading ? (
            <SectionsSkeleton />
          ) : (
            <>
              {sections?.map((section) => (
                <Tree
                  key={section.id}
                  section={section}
                  setEditingSectionId={setEditingSectionId}
                  setMovingSectionId={setMovingSectionId}
                />
              ))}
              <SidebarMenuItem>
                <Button
                  variant="ghost"
                  className="w-full justify-start"
                  onClick={() => setCreatingSection(true)}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add section
                </Button>
              </SidebarMenuItem>
            </>
          )}
        </SidebarMenu>
      </SidebarGroup>
      {editingSectionId && (
        <EditSectionDialog
          isOpened={!!editingSectionId}
          onOpenChange={(open) =>
            setEditingSectionId(open ? editingSectionId : null)
          }
          section={findSectionById(sections, editingSectionId)}
          onSubmit={handleSectionEdit}
        />
      )}
      {movingSectionId && (
        <MoveSectionDialog
          isOpened={!!movingSectionId}
          onOpenChange={(open) =>
            setMovingSectionId(open ? movingSectionId : null)
          }
          section={findSectionById(sections, movingSectionId)}
          onSubmit={handleSectionMove}
        />
      )}
      {creatingSection && (
        <CreateSectionDialog
          isOpened={creatingSection}
          onOpenChange={setCreatingSection}
          onSubmit={handleSectionCreate}
        />
      )}
    </>
  );
}

interface TreeProps {
  section: SectionResponse;
  noIndent?: boolean;
  setEditingSectionId: (id: string | null) => void;
  setMovingSectionId: (id: string | null) => void;
}

function Tree({
  section,
  noIndent = false,
  setEditingSectionId,
  setMovingSectionId,
}: TreeProps) {
  const hasChildren = section.subsections && section.subsections.length > 0;
  if (!hasChildren) {
    return (
      <SidebarMenuItem key={section.id}>
        <TreeElement
          section={section}
          withChevron={false}
          clickable={true}
          withIdentIfNoChevron={!noIndent}
          setEditingSectionId={setEditingSectionId}
          setMovingSectionId={setMovingSectionId}
        />
      </SidebarMenuItem>
    );
  }
  const anyChildHasChildren = section.subsections.some(
    (child: SectionResponse) => child.subsections.length > 0
  );

  return (
    <SidebarMenuItem key={section.title}>
      <Collapsible className="group" defaultOpen={true}>
        <div className="flex items-center">
          <CollapsibleTrigger asChild>
            <TreeElement
              section={section}
              withChevron={true}
              clickable={false}
              setEditingSectionId={setEditingSectionId}
              setMovingSectionId={setMovingSectionId}
            />
          </CollapsibleTrigger>
        </div>
        <CollapsibleContent>
          <SidebarMenuSub className="w-full">
            {section.subsections.map((child: SectionResponse) => (
              <Tree
                key={child.id}
                section={child}
                noIndent={!anyChildHasChildren}
                setEditingSectionId={setEditingSectionId}
                setMovingSectionId={setMovingSectionId}
              />
            ))}
          </SidebarMenuSub>
        </CollapsibleContent>
      </Collapsible>
    </SidebarMenuItem>
  );
}

interface TreeElementProps {
  section: SectionResponse;
  withChevron?: boolean;
  clickable?: boolean;
  withIdentIfNoChevron?: boolean;
  setEditingSectionId: (id: string | null) => void;
  setMovingSectionId: (id: string | null) => void;
}

const TreeElement = ({
  section,
  clickable = true,
  withChevron = false,
  withIdentIfNoChevron = true,
  setEditingSectionId,
  setMovingSectionId,
  ...props
}: TreeElementProps) => {
  const displayFullIdent = !withChevron && withIdentIfNoChevron;
  const displayMiniIdent = !withChevron && !withIdentIfNoChevron;
  const router = useRouter();

  const handleClick = () => {
    if (clickable) {
      router.push(`/section/${section.id}`);
    }
  };

  return (
    <SidebarMenuButton onClick={handleClick}>
      <ContextMenu>
        <ContextMenuTrigger>
          <div className="flex items-center w-full h-full" {...props}>
            {displayFullIdent && <div className="w-5 flex justify-left" />}
            {displayMiniIdent && <div className="w-2.5 flex justify-left" />}
            {withChevron && (
              <div className="w-5 flex justify-left">
                <ChevronRight className="transition-transform w-4 group-data-[state=open]:rotate-90" />
              </div>
            )}
            <div className="flex-grow ">
              <span>{section.title}</span>
            </div>
          </div>
        </ContextMenuTrigger>
        <ContextMenuContent>
          <ContextMenuItem
            onClick={(e) => {
              e.stopPropagation();
              setEditingSectionId(section.id);
            }}
          >
            <div className="flex items-center gap-x-2.5 cursor-pointer">
              <Pencil size={16} />
              Edit
            </div>
          </ContextMenuItem>
          <ContextMenuItem
            onClick={(e) => {
              e.stopPropagation();
              setMovingSectionId(section.id);
            }}
          >
            <div className="flex items-center gap-x-2.5 cursor-pointer">
              <ArrowDownUp size={16} />
              Move
            </div>
          </ContextMenuItem>
          <ContextMenuItem>
            <div className="flex items-center gap-x-2.5 cursor-pointer">
              <Trash size={16} />
              Remove
            </div>
          </ContextMenuItem>
        </ContextMenuContent>
      </ContextMenu>
    </SidebarMenuButton>
  );
};

function SectionsSkeleton() {
  return (
    <div className="space-y-4 space-x-4 px-5">
      <div className="flex items-center space-x-4">
        <Skeleton className="h-6 w-6 rounded" />
        <Skeleton className="h-4 w-[120px]" />
      </div>

      <div className="space-y-2">
        <div className="flex items-center space-x-4">
          <Skeleton className="h-6 w-6 rounded" />
          <Skeleton className="h-4 w-[120px]" />
        </div>
        <div className="ml-8 space-y-2">
          <Skeleton className="h-4 w-[80px]" />
          <Skeleton className="h-4 w-[80px]" />
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <Skeleton className="h-6 w-6 rounded" />
        <Skeleton className="h-4 w-[120px]" />
      </div>

      <div className="space-y-2">
        <div className="flex items-center space-x-4">
          <Skeleton className="h-6 w-6 rounded" />
          <Skeleton className="h-4 w-[120px]" />
        </div>
        <div className="ml-8 space-y-2">
          <div className="flex items-center space-x-4">
            <Skeleton className="h-6 w-6 rounded" />
            <Skeleton className="h-4 w-[80px]" />
          </div>
          <div className="flex items-center space-x-4">
            <Skeleton className="h-6 w-6 rounded" />
            <Skeleton className="h-4 w-[80px]" />
          </div>
          <div className="flex items-center space-x-4">
            <Skeleton className="h-6 w-6 rounded" />
            <Skeleton className="h-4 w-[80px]" />
          </div>
          <div className="flex items-center space-x-4">
            <Skeleton className="h-6 w-6 rounded" />
            <Skeleton className="h-4 w-[150px]" />
          </div>
        </div>
      </div>
    </div>
  );
}

function findSectionById(
  sections: SectionResponse[] | undefined,
  id: string
): SectionResponse {
  if (!sections) throw new Error("Sections are undefined");

  for (const section of sections) {
    if (section.id === id) {
      return section;
    }

    if (section.subsections) {
      const found = findSectionById(section.subsections, id);
      if (found) {
        return found;
      }
    }
  }

  throw new Error("Section with id " + id + " not found");
}
