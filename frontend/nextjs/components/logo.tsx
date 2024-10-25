import Image from "next/image";

export function Logo() {
  return (
    <div className="flex justify-center w-full">
      <div className="w-32">
        <Image
          src="/logo.png"
          className="w-full h-auto "
          width={200}
          height={200}
          alt="Planty logo"
        />
      </div>
    </div>
  );
}
