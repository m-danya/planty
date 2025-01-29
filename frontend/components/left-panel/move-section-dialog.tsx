"use client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useRef } from "react";
import { SectionMoveDialogForm } from "./section-move-dialog-form";
import { SectionResponse } from "@/api/Api";

interface MoveSectionDialogProps {
  isOpened: boolean;
  onOpenChange: (open: boolean) => void;
  section: SectionResponse;
  onSubmit: (updateSectionData: { parentId: string; index: number }) => void;
}

export function MoveSectionDialog({
  isOpened,
  onOpenChange,
  section,
  onSubmit,
}: MoveSectionDialogProps) {
  const titleInputRef = useRef<HTMLInputElement>(null);
  const initialParentId = section.parent_id;
  const initialIndex = 0;

  const handleCancel = () => {
    onOpenChange(false);
  };

  const handleSubmit = (updateSectionData: {
    parentId: string;
    index: number;
  }) => {
    onSubmit(updateSectionData);
    onOpenChange(false);
  };

  return (
    <Dialog open={isOpened} onOpenChange={onOpenChange}>
      <DialogContent
        onOpenAutoFocus={(event) => {
          // prevent selecting the title
          event.preventDefault();
          if (titleInputRef.current) {
            // focus on title (without selecting)
            // titleInputRef.current.focus();
            // NOTE: somewhat is selecting it again... why.. Couldn't fix it by
            // using context/providers, by using onOpenAutoFocus={(e) =>
            // e.preventDefault()} on SheetContent and by using <span
            // tabindex="0"></span>
          }
        }}
      >
        <DialogHeader>
          <DialogTitle>Move Section</DialogTitle>
        </DialogHeader>
        <SectionMoveDialogForm
          // initialTitle={initialTitle}
          initialParentId={initialParentId || undefined}
          initialIndex={initialIndex}
          submitLabel="Move"
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          titleInputRef={titleInputRef}
        />
      </DialogContent>
    </Dialog>
  );
}
