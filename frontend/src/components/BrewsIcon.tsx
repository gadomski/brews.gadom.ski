import { Icon, type IconProps } from "@chakra-ui/react";

/**
 * The Shoes & Brews logo (a foamy beer glass on a rounded teal tile) as a
 * Chakra `Icon`. It keeps its own multicolor palette, so the `color` prop does
 * not recolor it; use `size` or `boxSize` to scale it.
 */
export function BrewsIcon(props: IconProps) {
  return (
    <Icon asChild {...props}>
      <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="brewsGlass" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#FBC24A" />
            <stop offset="1" stopColor="#E68A1A" />
          </linearGradient>
        </defs>
        <rect x="0" y="0" width="100" height="100" rx="24" fill="#16545A" />
        <path
          d="M28 28 L72 28 L65 84 Q64 88 59 88 L41 88 Q36 88 35 84 Z"
          fill="url(#brewsGlass)"
          stroke="#10363A"
          strokeWidth="5"
          strokeLinejoin="round"
        />
        <path
          d="M25 29 Q22 15 32 14 Q33 5 44 9 Q50 1 58 8 Q70 4 71 16 Q80 18 75 29 Z"
          fill="#FFF6E6"
          stroke="#10363A"
          strokeWidth="5"
          strokeLinejoin="round"
        />
        <g stroke="#10363A" strokeWidth="4.6" strokeLinecap="round" fill="none">
          <line x1="38" y1="44" x2="62" y2="60" />
          <line x1="62" y1="44" x2="38" y2="60" />
          <line x1="39" y1="62" x2="61" y2="78" />
          <line x1="61" y1="62" x2="39" y2="78" />
        </g>
        <g fill="#10363A">
          <circle cx="38" cy="44" r="3" />
          <circle cx="62" cy="44" r="3" />
          <circle cx="38" cy="61" r="3" />
          <circle cx="62" cy="61" r="3" />
          <circle cx="39" cy="78" r="3" />
          <circle cx="61" cy="78" r="3" />
        </g>
      </svg>
    </Icon>
  );
}
