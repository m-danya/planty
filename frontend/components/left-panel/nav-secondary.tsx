import React from "react";

import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";

import Link from "next/link";
import { UserProfile } from "./user-profile";

export function NavSecondary({
  items,
  ...props
}: {
  items: {
    title: string;
    url: string;
    icon: React.ElementType;
    badge?: React.ReactNode;
  }[];
} & React.ComponentPropsWithoutRef<typeof SidebarGroup>) {
  const { setOpenMobile } = useSidebar();

  return (
    <SidebarGroup {...props}>
      <SidebarGroupContent>
        <SidebarMenu>
          {items.map((item) => (
            <SidebarMenuItem key={item.title}>
              <SidebarMenuButton asChild>
                <Link href={item.url} onClick={() => setOpenMobile(false)}>
                  <item.icon />
                  <span>{item.title}</span>
                </Link>
              </SidebarMenuButton>
              {item.badge && <SidebarMenuBadge>{item.badge}</SidebarMenuBadge>}
            </SidebarMenuItem>
          ))}

          <UserProfile />
          {/* <SidebarMenuItem key="user-profile-sidebar">
          {/* </SidebarMenuItem> */}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  );
}
