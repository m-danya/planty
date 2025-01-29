import { SVGProps } from "react";

interface SimpleIconProps extends SVGProps<SVGSVGElement> {
  icon: {
    svg: string;
  };
}

export function SimpleIcon({ icon, ...props }: SimpleIconProps) {
  return (
    <svg
      {...props}
      role="img"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      dangerouslySetInnerHTML={{ __html: icon.svg }}
    />
  );
}
