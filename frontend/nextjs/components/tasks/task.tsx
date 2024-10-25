import { Checkbox } from "@/components/ui/checkbox";

export function Task({ task }) {
  return (
    <div className="py-3.5 px-2 text-small">
      <div className="flex items-center justify-start w-full">
        <Checkbox className="mx-2 w-5 h-5 rounded-xl" />
        <div className="flex flex-col items-center">{task.name}</div>
      </div>
      {task.description && (
        <div className="ml-9 text-gray-400 pt-0.5">{task.description}</div>
      )}
    </div>
  );
}
