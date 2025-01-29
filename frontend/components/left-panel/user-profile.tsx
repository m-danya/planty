import { Button } from "@/components/ui/button";
import useUser from "@/hooks/use-user";
import { User } from "lucide-react";
import { useRouter } from "next/navigation";
import { SidebarMenuButton } from "@/components/ui/sidebar";

export function UserProfile() {
  const router = useRouter();
  const { user } = useUser();

  const handleLogout = async () => {
    try {
      await fetch("/api/auth/logout", {
        method: "POST",
      });
      router.push("/login");
    } catch (error) {
      console.error("Error while trying to logout:", error);
    }
  };

  if (!user) {
    return null;
  }

  return (
    <>
      <SidebarMenuButton asChild className="mt-4">
        <span>
          <User />
          <span>{user?.email}</span>
        </span>
      </SidebarMenuButton>
      <SidebarMenuButton asChild>
        <Button variant="ghost" className="w-fit" onClick={handleLogout}>
          Logout
        </Button>
      </SidebarMenuButton>
    </>
  );
}
