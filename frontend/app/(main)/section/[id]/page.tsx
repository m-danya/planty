import { TaskList } from "@/components/tasks/task-list";

export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params;
  return <TaskList sectionId={id} />;
}
