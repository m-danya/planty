"use client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useRef } from "react";
import { SectionEditDialogForm } from "./section-edit-dialog-form";

interface EditSectionDialogProps {
  isOpened: boolean;
  onOpenChange: (open: boolean) => void;
  section: {
    id: string;
    title: string;
  };
  onSubmit: (section: any) => void;
}

export function EditSectionDialog({
  isOpened,
  onOpenChange,
  section,
  onSubmit,
}: EditSectionDialogProps) {
  const initialTitle = section.title || "";

  const titleInputRef = useRef<HTMLInputElement>(null);

  const handleCancel = () => {
    onOpenChange(false);
  };

  const handleSubmit = (updatedSection: { title: string }) => {
    onSubmit({
      id: section.id,
      title: updatedSection.title,
    });
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
          <DialogTitle>Edit Section</DialogTitle>
        </DialogHeader>
        <SectionEditDialogForm
          initialTitle={initialTitle}
          submitLabel="Save"
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          titleInputRef={titleInputRef}
        />
      </DialogContent>
    </Dialog>
  );
}
