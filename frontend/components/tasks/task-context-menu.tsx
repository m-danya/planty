"use client";

import React from "react";
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
} from "@/components/ui/context-menu";
import { MoveRight, Archive } from "lucide-react";

interface TaskContextMenuProps {
  onOpenMoveDialog: () => void;
  onContextMenuChange: (open: boolean) => void;
  children: React.ReactNode;
}

export function TaskContextMenu({
  onOpenMoveDialog,
  onContextMenuChange,
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
        <ContextMenuItem>
          <div className="flex items-center gap-x-2.5 cursor-pointer">
            <Archive size={16} />
            Archive
          </div>
        </ContextMenuItem>
      </ContextMenuContent>
    </ContextMenu>
  );
}
