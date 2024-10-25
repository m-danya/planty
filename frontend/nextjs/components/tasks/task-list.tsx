import { Task } from "@/components/tasks/task";

const tasks = [
  { name: "Watch 'BoJack Horseman'" },
  { name: "Task with description", description: "some description here" },
  { name: "Clean the house" },
  { name: "Some completed archived task" },
  { name: "Go to the gym", description: "💪🏻💪🏻💪🏻" },
  { name: "A task with date", date: "2024-12-28" },
];

export function TaskList() {
  return (
    <div className="items-center flex-col">
      <div className="xl:px-40">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold md:text-2xl">Tasks</h1>
        </div>
        <div className="flex flex-col py-4">
          {tasks.map((task) => (
            <>
              <div>
                <Task task={task} />
              </div>
              <hr className="border-gray-200 dark:border-white" />
            </>
          ))}
        </div>
      </div>
    </div>
  );
}
