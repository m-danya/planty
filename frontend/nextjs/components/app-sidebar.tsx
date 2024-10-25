"use client";

import {
  Archive,
  Calendar,
  Search,
  Settings2,
  Sparkles,
  User,
} from "lucide-react";
import * as React from "react";

import { siGithub } from "simple-icons";

import { NavMain } from "@/components/nav-main";
import { NavSecondary } from "@/components/nav-secondary";
import { NavSections } from "@/components/nav-sections";
import { SimpleIcon } from "@/components/simple-icon";
import { TeamSwitcher } from "@/components/team-switcher";
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar";

const data = {
  teams: [
    {
      name: "Name Surname",
      logo: User,
    },
  ],
  navMain: [
    {
      title: "Search",
      url: "#",
      icon: Search,
    },
    {
      title: "Ask AI",
      url: "#",
      icon: Sparkles,
    },
    {
      title: "Calendar",
      url: "#",
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
      url: "#",
      icon: Archive,
    },
    {
      title: "Project home",
      url: "https://github.com/m-danya/planty",
      icon: () => <SimpleIcon icon={siGithub} />,
    },
  ],
  favorites: [
    {
      name: "Inbox",
      url: "#",
      emoji: "📩",
    },
    {
      name: "Current tasks",
      url: "#",
      emoji: "📝",
    },
    {
      name: "Projects",
      url: "#",
      emoji: "🎯",
    },
    {
      name: "Sometime later",
      url: "#",
      emoji: "📝",
      children: [
        {
          name: "Duties",
          url: "#",
          emoji: "💼",
        },
        {
          name: "Programming",
          url: "#",
          emoji: "💻",
        },
        {
          name: "Music",
          url: "#",
          emoji: "🎸",
        },
        {
          name: "Would be great to do",
          url: "#",
          emoji: "🦄",
        },
      ],
    },
    {
      name: "Waiting for others",
      url: "#",
      emoji: "⌛",
    },
  ],
  workspaces: [],
};

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar className="border-r-0" {...props}>
      <SidebarHeader>
        <TeamSwitcher teams={data.teams} />
        <NavMain items={data.navMain} />
      </SidebarHeader>
      <SidebarContent>
        <NavSections sections={data.favorites} />
        <NavSecondary items={data.navSecondary} className="mt-auto" />
      </SidebarContent>
      <SidebarRail />
    </Sidebar>
  );
}
