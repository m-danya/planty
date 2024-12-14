"use client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useRef } from "react";
import { SectionDialogForm } from "./section-dialog-form";

interface EditSectionDialogProps {
  isEditing: boolean;
  onOpenChange: (open: boolean) => void;
  section: {
    id: string;
    title: string;
  };
  handleSectionEdit: (section: any) => void;
}

export function EditSectionDialog({
  isEditing,
  onOpenChange,
  section,
  handleSectionEdit,
}: EditSectionDialogProps) {
  const initialTitle = section.title || "";
  // TODO: add parentSectionId and index
  const titleInputRef = useRef<HTMLInputElement>(null);

  const handleCancel = () => {
    onOpenChange(false);
  };

  const handleSubmit = (updatedSection: { title: string }) => {
    handleSectionEdit({
      id: section.id,
      title: updatedSection.title,
    });
    onOpenChange(false);
  };

  return (
    <Dialog open={isEditing} onOpenChange={onOpenChange}>
      <DialogContent
        onOpenAutoFocus={(event) => {
          // prevent selecting the title
          event.preventDefault();
          if (titleInputRef.current) {
            // focus on title (without selecting)
            titleInputRef.current.focus();
            // TODO FIX: somewhat is selecting it again... why..
          }
        }}
      >
        <DialogHeader>
          <DialogTitle>Edit Section</DialogTitle>
        </DialogHeader>
        <SectionDialogForm
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
