// move-task-dialog.tsx

"use client";

import { Api } from "@/api/Api";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { useSections } from "@/hooks/use-sections";
import { cn } from "@/lib/utils";
import { zodResolver } from "@hookform/resolvers/zod";
import { Check, ChevronsUpDown } from "lucide-react";
import React from "react";
import { useForm } from "react-hook-form";
import * as z from "zod";

interface MoveTaskDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  taskTitle: string;
  taskId: string;
  mutateOnTaskMove: () => void;
}

const formSchema = z.object({
  sectionId: z.string().nonempty("Please select a section"),
});

export function MoveTaskDialog({
  open,
  onOpenChange,
  taskTitle,
  taskId,
  mutateOnTaskMove,
}: MoveTaskDialogProps) {
  const { sections, isLoading, isError } = useSections({
    leavesOnly: true,
  });
  const api = new Api().api;
  const [comboboxOpen, setComboboxOpen] = React.useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      sectionId: "",
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    try {
      const result = await api.moveTaskApiTaskMovePost({
        task_id: taskId,
        section_to_id: values.sectionId,
        index: 0, // TODO: pass None to move to the end of section
      });
      console.log("Task moved successfully:", result);
      mutateOnTaskMove();
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
          <DialogTitle>
            Move &quot;{taskTitle}&quot; to another section
          </DialogTitle>
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
                  <Popover open={comboboxOpen} onOpenChange={setComboboxOpen}>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        role="combobox"
                        aria-expanded={comboboxOpen}
                        className="w-full justify-between"
                      >
                        {field.value
                          ? sections?.find(
                              (section) => section.id === field.value
                            )?.title
                          : "Select section..."}
                        <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-full p-0">
                      <Command>
                        <CommandInput placeholder="Search section..." />
                        <CommandList>
                          <CommandEmpty>No section found.</CommandEmpty>
                          <CommandGroup>
                            {isLoading && (
                              <CommandItem disabled>
                                Loading sections...
                              </CommandItem>
                            )}
                            {isError && (
                              <CommandItem disabled>
                                Error loading sections
                              </CommandItem>
                            )}
                            {!isLoading &&
                              sections?.map((section) => (
                                <CommandItem
                                  key={section.id}
                                  value={section.title}
                                  onSelect={() => {
                                    field.onChange(section.id);
                                    setComboboxOpen(false);
                                  }}
                                >
                                  <Check
                                    className={cn(
                                      "mr-2 h-4 w-4",
                                      field.value === section.id
                                        ? "opacity-100"
                                        : "opacity-0"
                                    )}
                                  />
                                  {section.title}
                                </CommandItem>
                              ))}
                          </CommandGroup>
                        </CommandList>
                      </Command>
                    </PopoverContent>
                  </Popover>
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
