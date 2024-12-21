"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import React, { forwardRef, useState } from "react";

interface SectionEditDialogFormProps {
  initialTitle?: string;
  submitLabel: string;
  onSubmit: (section: { title: string }) => void;
  onCancel: () => void;
  titleInputRef?: React.RefObject<HTMLInputElement>;
}

export const SectionEditDialogForm = forwardRef<
  HTMLInputElement,
  SectionEditDialogFormProps
>(
  (
    { initialTitle = "", submitLabel, onSubmit, onCancel, titleInputRef },
    ref
  ) => {
    const [title, setTitle] = useState(initialTitle);

    const handleFinish = (e: React.FormEvent) => {
      e.preventDefault();
      onSubmit({
        title,
      });
    };

    return (
      <div>
        <form
          onSubmit={handleFinish}
          className="space-y-4 mt-4"
          autoComplete="off"
        >
          <div>
            <Label htmlFor="section_title">Title</Label>
            <Input
              id="section_title"
              ref={titleInputRef}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>

          <div className="flex justify-end space-x-2">
            <Button variant="outline" onClick={onCancel} type="button">
              Cancel
            </Button>
            <Button type="submit">{submitLabel}</Button>
          </div>
        </form>
      </div>
    );
  }
);

SectionEditDialogForm.displayName = "SectionDialogForm"; // for devtools
