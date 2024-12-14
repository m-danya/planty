// move-task-dialog.tsx

"use client";

import React from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Api, SectionResponse } from "@/api/Api";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useSections } from "@/hooks/use-sections";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";

interface MoveTaskDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  taskTitle: string;
  taskId: string;
  mutateSection: () => void;
}

const formSchema = z.object({
  sectionId: z.string().nonempty("Please select a section"),
});

export function MoveTaskDialog({
  open,
  onOpenChange,
  taskTitle,
  taskId,
  mutateSection,
}: MoveTaskDialogProps) {
  const { sections, isLoading, isError } = useSections({
    leavesOnly: true,
  });
  const api = new Api().api;

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      sectionId: "",
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    console.log(values);
    try {
      const result = await api.moveTaskApiTaskMovePost({
        task_id: taskId,
        section_to_id: values.sectionId,
        index: 0, // TODO: pass None to move to the end of section
      });
      console.log("Task moved successfully:", result);
      mutateSection();
      onOpenChange(false);
    } catch (error) {
      console.error("Failed to move task:", error);
      alert("Failed to move task");
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Move "{taskTitle}" to another section</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form
            noValidate
            onSubmit={form.handleSubmit(onSubmit)}
            className="space-y-8"
            autoComplete="off"
          >
            <FormField
              control={form.control}
              name="sectionId"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Section</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    value={field.value}
                    defaultValue={field.value}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select section" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {isLoading && (
                        <SelectItem disabled>Loading sections...</SelectItem>
                      )}
                      {isError && (
                        <SelectItem disabled>Error loading sections</SelectItem>
                      )}
                      {!isLoading &&
                        sections?.map((section: SectionResponse) => (
                          <SelectItem value={section.id} key={section.id}>
                            {section.title}
                          </SelectItem>
                        ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit">Submit</Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
