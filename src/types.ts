import type { ImageMetadata } from 'astro';

// Interface for general Call to Action items (buttons, links)
export interface CallToAction {
  text: string;
  href: string;
  variant?: 'primary' | 'secondary' | 'tertiary' | 'link';
  // The following properties are used by Button.astro
  target?: string;
  icon?: string;
  class?: string;
  // Any other properties are passed through to the button/link
  [key: string]: unknown; // Changed from 'any' to 'unknown' for better type safety
}

// Interface for Hero section properties
export interface Hero {
  title?: string;
  subtitle?: string;
  tagline?: string;
  content?: string;
  actions?: Array<CallToAction>; // Array of CallToAction objects
  image?: string | { src: string | ImageMetadata | Promise<{ default: ImageMetadata }>; alt: string };
  id?: string;
  bg?: string; // Background slot content
}

// Interface for blog post metadata
export interface Post {
  id?: string;
  slug?: string;
  publishDate: Date;
  title: string;
  excerpt?: string;
  image?: string | ImageMetadata;
  category?: {
    title: string;
    slug: string;
  };
  tags?: Array<{
    title: string;
    slug: string;
  }>;
  author?: string;
  readingTime?: number;
  draft?: boolean;
  metadata?: {
    canonical?: string;
  };
}

// You can add other shared type definitions here as needed
// For example:
// export interface Header {
//   links?: Array<{ text: string; href: string }>;
//   actions?: Array<CallToAction>;
// }

// export interface Footer {
//   // ... footer properties
// }
