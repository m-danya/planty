import { TaskList } from "@/components/tasks/task-list";

export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id: sectionId } = await params;
  // TODO: fetch initial data here to avoid flickering?
  return <TaskList sectionId={sectionId} />;
}
