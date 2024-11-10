import React from "react";
import Image from "next/image";

function NoSectionSelected() {
  return (
    <div className="flex justify-center w-full h-full items-center opacity-[.12]">
      <div className="w-20 ">
        <Image
          src="/sign_black_stroke.png"
          className="w-full h-auto "
          width={200}
          height={200}
          alt="Planty logo"
        />
      </div>
    </div>
  );
}

export default NoSectionSelected;
