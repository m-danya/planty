"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useSections } from "@/hooks/use-sections";
import React, { forwardRef, useState } from "react";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface SectionMoveDialogFormProps {
  initialParentId?: string;
  initialIndex?: number;
  submitLabel: string;
  onSubmit: (section) => void;
  onCancel: () => void;
  titleInputRef?: React.RefObject<HTMLInputElement>;
}

export const SectionMoveDialogForm = forwardRef<
  HTMLInputElement,
  SectionMoveDialogFormProps
>(
  (
    {
      initialParentId,
      initialIndex,
      submitLabel,
      onSubmit,
      onCancel,
      titleInputRef,
    },
    ref
  ) => {
    const [parentId, setParentId] = useState(initialParentId);
    const [index, setIndex] = useState(initialIndex);

    const {
      sections,
      rootSectionId,
      isLoading,
      isError,
      // mutate: mutateSections,
    } = useSections({ asTree: false });
    const handleFinish = (e: React.FormEvent) => {
      e.preventDefault();
      onSubmit({
        parentId,
        index,
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
            <Label htmlFor="section_parent">Parent section</Label>

            <Select value={parentId} onValueChange={setParentId}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Parent section" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectLabel>Parent section</SelectLabel>
                  {rootSectionId && (
                    <SelectItem key="rootSection" value={rootSectionId}>
                      No parent section
                    </SelectItem>
                  )}
                  {sections
                    ?.filter(
                      (s) => !!s.parent_id // filter out root section
                    )
                    .map((section) => (
                      <SelectItem key={section.id} value={section.id}>
                        {section.title}
                      </SelectItem>
                    ))}
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="section_index">Index in parent section</Label>
            <Input
              id="section_index"
              value={index}
              onChange={(e) => setIndex(e.target.value)}
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

SectionMoveDialogForm.displayName = "SectionDialogForm"; // for devtools
