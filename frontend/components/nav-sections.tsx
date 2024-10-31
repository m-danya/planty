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
import React from "react";

import { useSections } from "@/hooks/use-sections";

export function NavSections() {
  const { sections, isLoading, isError } = useSections();
  if (isLoading) return <p>Loading sections...</p>;
  if (isError) return <p>Failed to load sections.</p>;
  return (
    <SidebarGroup className="group-data-[collapsible=icon]:hidden">
      <SidebarGroupLabel>Sections</SidebarGroupLabel>
      <SidebarMenu>
        {sections.map((item) => (
          <Tree key={item.title} item={item} />
        ))}
      </SidebarMenu>
    </SidebarGroup>
  );
}

function Tree({ item }) {
  const hasChildren = item.subsections && item.subsections.length > 0;

  if (!hasChildren) {
    return (
      <SidebarMenuItem key={item.title}>
        <SidebarMenuButton asChild>
          <TreeElement item={item} />
        </SidebarMenuButton>
      </SidebarMenuItem>
    );
  }

  return (
    <SidebarMenuItem key={item.title}>
      <Collapsible
        className="group/collapsible [&[data-state=open]>div>button>svg:first-child]:rotate-90"
        defaultOpen={true}
      >
        <div className="flex items-center">
          <CollapsibleTrigger asChild>
            <SidebarMenuButton>
              <ChevronRight className="transition-transform" />
              <span>{item.emoji}</span>
              <span>{item.title}</span>
            </SidebarMenuButton>
          </CollapsibleTrigger>
        </div>
        <CollapsibleContent>
          <SidebarMenuSub className="w-fit">
            {item.subsections.map((child) => (
              <Tree key={child.title} item={child} />
            ))}
          </SidebarMenuSub>
        </CollapsibleContent>
      </Collapsible>
    </SidebarMenuItem>
  );
}

const TreeElement = React.forwardRef(({ item, ...props }, ref) => (
  <a ref={ref} href={`/section/${item.id}`} title={item.title} {...props}>
    <span>{item.title}</span>
  </a>
));
