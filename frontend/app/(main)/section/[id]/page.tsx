import { Section } from "@/components/tasks/section";

export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id: sectionId } = await params;
  // TODO: fetch initial data here to avoid flickering?
  return <Section sectionId={sectionId} />;
}
