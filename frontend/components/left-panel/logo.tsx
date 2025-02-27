import Image from "next/image";
import Link from "next/link";
import { useSidebar } from "@/components/ui/sidebar";

export function Logo() {
  const { setOpenMobile } = useSidebar();

  return (
    <div className="flex justify-center w-full">
      <div className="w-40">
        <Link href="/" onClick={() => setOpenMobile(false)}>
          <Image
            src="/logo_hor.png"
            className="w-full h-auto"
            width={200}
            height={200}
            alt="Planty logo"
          />
        </Link>
      </div>
    </div>
  );
}
