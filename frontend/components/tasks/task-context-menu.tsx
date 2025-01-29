"use client";

import React from "react";
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
} from "@/components/ui/context-menu";
import { MoveRight, Archive, ArchiveRestore } from "lucide-react";
import { TaskResponse } from "@/api/Api";

interface TaskContextMenuProps {
  task: TaskResponse;
  onOpenMoveDialog: () => void;
  onContextMenuChange: (open: boolean) => void;
  onToggleArchived: () => void;
  children: React.ReactNode;
}

export function TaskContextMenu({
  task,
  onOpenMoveDialog,
  onContextMenuChange,
  onToggleArchived,
  children,
}: TaskContextMenuProps) {
  return (
    <ContextMenu onOpenChange={onContextMenuChange}>
      <ContextMenuTrigger>{children}</ContextMenuTrigger>
      <ContextMenuContent>
        <ContextMenuItem>
          <div
            className="flex items-center gap-x-2.5 cursor-pointer"
            onClick={onOpenMoveDialog}
          >
            <MoveRight size={16} />
            Move to another section
          </div>
        </ContextMenuItem>
        {/* <ContextMenuItem>
          <div
            className="flex items-center gap-x-2.5 cursor-pointer pr-2"
            onClick={...}
          >
            <CircleCheck size={16} />
            Complete without archiving
          </div>
        </ContextMenuItem> */}

        <ContextMenuItem>
          <div
            className="flex items-center gap-x-2.5 cursor-pointer"
            onClick={onToggleArchived}
          >
            {task.is_archived && (
              <>
                <ArchiveRestore size={16} />
                Unarchive
              </>
            )}
            {!task.is_archived && (
              <>
                <Archive size={16} />
                Archive
              </>
            )}
          </div>
        </ContextMenuItem>
      </ContextMenuContent>
    </ContextMenu>
  );
}
