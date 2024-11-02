"use client";
import { AppSidebar } from "@/components/app-sidebar";
import { TaskList } from "@/components/tasks/task-list";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import useUser from "@/hooks/use-user";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function Page() {
  const router = useRouter();
  const { user, loading, loggedIn, mutate } = useUser();

  useEffect(() => {
    console.log(user, loading, loggedIn, mutate);
    if (!loggedIn) {
      router.push("/login");
    }
  }, [loggedIn]);
  if (!loggedIn) return "";

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
        <div className="flex flex-1 flex-col gap-4 px-4 py-10">
          <TaskList />
          {/* <div className="mx-auto h-full w-full max-w-3xl rounded-xl bg-muted/50" /> */}
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}
