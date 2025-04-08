import { getPermalink } from './utils/permalinks';

export const headerData = {
  links: [
    {
      text: 'Articles',
      href: getPermalink('/articles'),
    },
    {
      text: 'Community',
      href: getPermalink('/community'),
    },
  ],
  actions: [
    {
      text: 'AI Healthcheck',
      href: getPermalink('/ai-healthcheck'),
      variant: 'primary',
    },
  ],
};

export const footerData = {
  links: [
    {
      title: 'Services',
      links: [
        { text: 'AI Healthcheck', href: getPermalink('/ai-healthcheck') },
        { text: 'Articles', href: getPermalink('/articles') },
        { text: 'Community', href: getPermalink('/community') },
      ],
    },
  ],
  secondaryLinks: [
    { text: 'Terms', href: getPermalink('/terms') },
    { text: 'Privacy', href: getPermalink('/privacy') },
    { text: 'Cookie', href: getPermalink('/cookie-policy') },
  ],
  socialLinks: [
    { ariaLabel: 'LinkedIn', icon: 'tabler:brand-linkedin', href: 'https://www.linkedin.com/in/samirabid/' },
  ],
  footNote: `
    <span class="w-5 h-5 md:w-6 md:h-6 md:-mt-0.5 bg-cover mr-1.5 rtl:mr-0 rtl:ml-1.5 float-left rtl:float-right rounded-sm"></span>
    Made by <a class="text-blue-600 hover:underline dark:text-gray-200" href="https://paceinsights.com/"> Pace Insights</a> · All rights reserved.
  `,
};
