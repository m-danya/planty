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

export function NavSections({
  sections,
}: {
  sections: {
    name: string;
    url: string;
    emoji: string;
    children?: any[];
  }[];
}) {
  return (
    <SidebarGroup className="group-data-[collapsible=icon]:hidden">
      <SidebarGroupLabel>Sections</SidebarGroupLabel>
      <SidebarMenu>
        {sections.map((item) => (
          <Tree key={item.name} item={item} />
        ))}
      </SidebarMenu>
    </SidebarGroup>
  );
}

function Tree({ item }) {
  const hasChildren = item.children && item.children.length > 0;

  if (!hasChildren) {
    return (
      <SidebarMenuItem key={item.name}>
        <SidebarMenuButton asChild>
          <TreeElement item={item} />
        </SidebarMenuButton>
      </SidebarMenuItem>
    );
  }

  return (
    <SidebarMenuItem key={item.name}>
      <Collapsible className="group/collapsible [&[data-state=open]>div>button>svg:first-child]:rotate-90">
        <div className="flex items-center">
          <CollapsibleTrigger asChild>
            <SidebarMenuButton>
              <ChevronRight className="transition-transform" />
              <span>{item.emoji}</span>
              <span>{item.name}</span>
            </SidebarMenuButton>
          </CollapsibleTrigger>
        </div>
        <CollapsibleContent>
          <SidebarMenuSub className="w-fit">
            {item.children.map((child) => (
              <Tree key={child.name} item={child} />
            ))}
          </SidebarMenuSub>
        </CollapsibleContent>
      </Collapsible>
    </SidebarMenuItem>
  );
}

const TreeElement = React.forwardRef(({ item, ...props }, ref) => (
  <a ref={ref} href={item.url} title={item.name} {...props}>
    <span>{item.emoji}</span>
    <span>{item.name}</span>
  </a>
));
