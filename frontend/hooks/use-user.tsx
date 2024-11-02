import useSWR from "swr";
import { fetcher } from "@/hooks/fetcher";

export default function useUser() {
  const { data, mutate, error } = useSWR("/api/auth/me", fetcher);

  const loading = !data && !error;
  console.log(error);
  const loggedIn = !(error && error.status === 401);

  return {
    loading,
    loggedIn,
    user: data,
    mutate,
  };
}
