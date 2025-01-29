"use client";

import { MainSidebarWrapper } from "@/components/left-panel/main-sidebar-wrapper";
import { useAuthRedirect } from "@/hooks/use-auth-redirect";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  useAuthRedirect();

  return <MainSidebarWrapper>{children}</MainSidebarWrapper>;
}
