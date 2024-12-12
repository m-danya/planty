import { MainSidebarWrapper } from "@/components/left-panel/main-sidebar-wrapper";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return <MainSidebarWrapper>{children}</MainSidebarWrapper>;
}
