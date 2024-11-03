"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import useUser from "@/hooks/use-user";

export function useAuthRedirect() {
  const router = useRouter();
  const { user, loading, loggedIn, mutate } = useUser();

  useEffect(() => {
    if (!loggedIn && !loading) {
      router.push("/login");
    }
  }, [loggedIn, loading, router]);

  return { mutate };
}
