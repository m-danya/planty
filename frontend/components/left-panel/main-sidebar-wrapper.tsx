"use client";
import { AppSidebar } from "@/components/left-panel/app-sidebar";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";

export function MainSidebarWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="flex h-14 shrink-0 items-center gap-2">
          <div className="flex flex-1 items-center gap-2 px-3">
            <SidebarTrigger />
          </div>
          <div className="ml-auto px-3">{/* <NavActions /> */}</div>
        </header>
        <div>{children}</div>
      </SidebarInset>
    </SidebarProvider>
  );
}
