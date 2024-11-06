import { MainSidebarWrapper } from "@/components/main-sidebar-wrapper";


export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
        <MainSidebarWrapper>{children}</MainSidebarWrapper>
  );
}
