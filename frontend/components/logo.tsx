import Image from "next/image";

export function Logo() {
  return (
    <div className="flex justify-center w-full">
      <div className="w-40">
        <Image
          src="/logo_hor.png"
          className="w-full h-auto "
          width={200}
          height={200}
          alt="Planty logo"
        />
      </div>
    </div>
  );
}
