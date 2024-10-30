import { AppSidebar } from "@/components/app-sidebar";
import { NavActions } from "@/components/nav-actions";
import { TaskList } from "@/components/tasks/task-list";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbPage,
} from "@/components/ui/breadcrumb";
import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";

export default function Page() {
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