import { moveTask } from "@/app/services/taskService";
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

const formSchema = z.object({ sectionId: z.string() });

export function MoveTaskToSectionForm({
  taskId,
  afterSubmit,
}: {
  taskId: string;
  afterSubmit: () => void;
}) {
  const { sections, isLoading, isError } = useSections({
    leavesOnly: true,
  });
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {},
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    console.log(values);
    const moveTaskData = {
      task_id: taskId,
      section_to_id: values.sectionId,
      index: 0, // TODO: pass None to move to the end of section
    };
    try {
      const result = await moveTask(moveTaskData);
      console.log("Task moved successfully:", result);
    } catch (error) {
      console.error("Failed to move task:", error);
      console.log("Failed to move task");
    }
    afterSubmit();
  }

  return (
    <Form {...form}>
      <form
        noValidate
        onSubmit={form.handleSubmit(onSubmit)}
        className="space-y-8"
      >
        <FormField
          control={form.control}
          name="sectionId"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Section</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select section" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {!isLoading &&
                    sections.map((section) => (
                      <SelectItem value={section.id} key={section.id}>
                        {section.title}
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />{" "}
        <Button type="submit">Submit</Button>
      </form>
    </Form>
  );
}
