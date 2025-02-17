"use client";

import { Archive, Calendar, Search, Settings2 } from "lucide-react";
import * as React from "react";

import { siGithub } from "simple-icons";

import { NavMain } from "@/components/left-panel/nav-main";
import { NavSecondary } from "@/components/left-panel/nav-secondary";
import { NavSections } from "@/components/left-panel/nav-sections";
import { Logo } from "@/components/left-panel/logo";
import { SimpleIcon } from "@/components/simple-icon";
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar";

const data = {
  navMain: [
    {
      title: "Search",
      url: "#",
      icon: Search,
    },
    // {
    //   title: "Ask AI",
    //   url: "#",
    //   icon: Sparkles,
    // },
    {
      title: "Calendar",
      url: "/calendar",
      icon: Calendar,
    },
  ],
  navSecondary: [
    {
      title: "Settings",
      url: "#",
      icon: Settings2,
    },
    {
      title: "Archived tasks",
      url: "/archived",
      icon: Archive,
    },
    {
      title: "Project home",
      url: "https://github.com/m-danya/planty",
      icon: () => <SimpleIcon icon={siGithub} />,
    },
  ],
};

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar className="border-r-0" {...props}>
      <SidebarHeader>
        <Logo />
        <NavMain items={data.navMain} />
      </SidebarHeader>
      <SidebarContent>
        <NavSections />
        <NavSecondary items={data.navSecondary} className="mt-auto" />
      </SidebarContent>
      <SidebarRail />
    </Sidebar>
  );
}
