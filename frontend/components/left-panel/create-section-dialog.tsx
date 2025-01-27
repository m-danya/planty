"use client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { SectionEditDialogForm } from "./section-edit-dialog-form";
import { useRef } from "react";

interface CreateSectionDialogProps {
  isOpened: boolean;
  onOpenChange: (opened: boolean) => void;
  onSubmit: (section: { title: string }) => void;
}

export function CreateSectionDialog({
  isOpened,
  onOpenChange,
  onSubmit,
}: CreateSectionDialogProps) {
  const titleInputRef = useRef<HTMLInputElement>(null);

  return (
    <Dialog open={isOpened} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create new section</DialogTitle>
        </DialogHeader>
        <SectionEditDialogForm
          submitLabel="Create"
          onSubmit={(data) => {
            onSubmit(data);
            onOpenChange(false);
          }}
          onCancel={() => onOpenChange(false)}
          titleInputRef={titleInputRef}
        />
      </DialogContent>
    </Dialog>
  );
}
