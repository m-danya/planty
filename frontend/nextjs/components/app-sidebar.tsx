"use client";

import * as React from "react";
import {
  AudioWaveform,
  Blocks,
  Calendar,
  Command,
  Home,
  Inbox,
  MessageCircleQuestion,
  Search,
  Settings2,
  Sparkles,
  Origami,
  Trash2,
  Archive,
} from "lucide-react";

import { siGithub } from "simple-icons";

import { NavFavorites } from "@/components/nav-favorites";
import { NavMain } from "@/components/nav-main";
import { NavSecondary } from "@/components/nav-secondary";
import { TeamSwitcher } from "@/components/team-switcher";
import { SimpleIcon } from "@/components/simple-icon";
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar";

const data = {
  teams: [
    {
      name: "Dunder Mifflin",
      logo: Origami,
      plan: "free",
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
      title: "Inbox",
      url: "#",
      icon: Inbox,
      badge: "10",
    },
    {
      title: "Calendar",
      url: "#",
      icon: Calendar,
      badge: "10",
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
      name: "Current tasks",
      url: "#",
      emoji: "📝",
    },
    {
      name: "Sometime later",
      url: "#",
      emoji: "📚",
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
        <NavFavorites favorites={data.favorites} />
        <NavSecondary items={data.navSecondary} className="mt-auto" />
      </SidebarContent>
      <SidebarRail />
    </Sidebar>
  );
}
