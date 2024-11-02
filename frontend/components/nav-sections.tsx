"use client";

import { ChevronRight } from "lucide-react";

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
} from "@/components/ui/sidebar";
import { Skeleton } from "@/components/ui/skeleton";
import React from "react";

import { useSections } from "@/hooks/use-sections";

export function NavSections() {
  const { sections, rootSectionId, isLoading, isError } = useSections();

  if (isError) return <p>Failed to load sections.</p>;
  return (
    <SidebarGroup className="group-data-[collapsible=icon]:hidden text-nowrap">
      <SidebarGroupLabel>Sections</SidebarGroupLabel>
      <SidebarMenu>
        {isLoading ? (
          <SectionsSkeleton />
        ) : (
          sections.map((item) => <Tree key={item.title} item={item} />)
        )}
      </SidebarMenu>
    </SidebarGroup>
  );
}

function Tree({ item, noIndent = false }) {
  const hasChildren = item.subsections && item.subsections.length > 0;
  if (!hasChildren) {
    return (
      <SidebarMenuItem key={item.title}>
        <SidebarMenuButton>
          <TreeElement
            item={item}
            withChevron={false}
            clickable={true}
            withIdentIfNoChevron={!noIndent}
          />
        </SidebarMenuButton>
      </SidebarMenuItem>
    );
  }
  const anyChildHasChildren = item.subsections.some(
    (child) => child.subsections.length > 0
  );

  return (
    <SidebarMenuItem key={item.title}>
      <Collapsible className="group" defaultOpen={true}>
        <div className="flex items-center">
          <CollapsibleTrigger asChild>
            <SidebarMenuButton>
              <TreeElement item={item} withChevron={true} clickable={false} />
            </SidebarMenuButton>
          </CollapsibleTrigger>
        </div>
        <CollapsibleContent>
          <SidebarMenuSub className="w-fit">
            {item.subsections.map((child) => (
              <Tree
                key={child.title}
                item={child}
                noIndent={!anyChildHasChildren}
              />
            ))}
          </SidebarMenuSub>
        </CollapsibleContent>
      </Collapsible>
    </SidebarMenuItem>
  );
}

const TreeElement = React.forwardRef<
  HTMLAnchorElement,
  {
    item: { id: string; title: string };
    withChevron?: boolean;
    clickable?: boolean;
    withIdentIfNoChevron?: boolean;
  } & React.HTMLAttributes<HTMLAnchorElement>
>(
  (
    {
      item,
      clickable = true,
      withChevron = false,
      withIdentIfNoChevron = true,
      ...props
    },
    ref
  ) => {
    const displayFullIdent = !withChevron && withIdentIfNoChevron;
    const displayMiniIdent = !withChevron && !withIdentIfNoChevron;
    const mainContent = (
      <div className="flex items-center">
        {displayFullIdent && <div className="w-5 flex justify-left" />}
        {displayMiniIdent && <div className="w-2.5 flex justify-left" />}
        {withChevron && (
          <div className="w-5 flex justify-left">
            <ChevronRight className="transition-transform w-4 group-data-[state=open]:rotate-90" />
          </div>
        )}
        <div className="flex-grow ">
          <span>{item.title}</span>
        </div>
      </div>
    );
    if (!clickable) {
      return mainContent;
    } else {
      return (
        <a
          ref={ref}
          href={`/section/${item.id}`}
          title={item.title}
          {...props}
          className=""
        >
          {mainContent}
        </a>
      );
    }
  }
);

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
