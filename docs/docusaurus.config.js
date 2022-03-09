// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'UKP-SQuARE',
  tagline: 'Software for Question-Answering Research',
  url: 'https://square.ukp-lab.de',
  baseUrl: '/docs/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/SQ_Web_fav_160px.png',
  organizationName: 'UKP', // Usually your GitHub org/user name.
  projectName: 'square-core', // Usually your repo name.
  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          // Please change this to your repo.
          editUrl: 'https://github.com/UKP-SQuARE/square-core/tree/master/docs',
            path: 'home',
            routeBasePath: 'home',
        },
        blog: {
          showReadingTime: true,
          // Please change this to your repo.
          editUrl:
            'https://github.com/UKP-SQuARE/square-core/tree/master',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
      [
     "redocusaurus",
     {
       specs: [
           {
           routePath: "/api/datastores/",
           specUrl: "https://square.ukp-lab.de/api/datastores/openapi.json",
           },
           {
           routePath: "/api/skills/",
           specUrl: "https://square.ukp-lab.de/api/skill-manager/openapi.json",
          },
           {
           routePath: "/api/models-inference/",
           specUrl: "https://square.ukp-lab.de/api/facebook-dpr-question_encoder-single-nq-base/openapi.json",
          },
           {
           routePath: "/api/models-management/",
           specUrl: "https://square.ukp-lab.de/api/models/openapi.json",
          },
       ],
     },
   ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      announcementBar: {
          id: 'beta',
          content:
            'The <b>model management</b> service is currently in beta. The stable version will be released soon.',
          backgroundColor: '#fafbfc',
          textColor: '#091E42',
          isCloseable: true,
     },
      navbar: {
        title: 'UKP-SQuARE',
        logo: {
          alt: 'My Site Logo',
          src: 'img/SQ_Web_fav_160px.png',
        },
        items: [
          {
            type: 'doc',
            docId: 'overview/introduction',
            position: 'left',
            label: 'Overview',
          },
            {
            type: 'doc',
            docId: 'components/datastores',
            position: 'left',
            label: 'Components',
          },
            {
           label: 'API',
           position: 'left',
           items: [
             {
               label: 'Datastores',
               to: '/api/datastores/',
             },
             {
               label: 'Models-Inference',
               to: '/api/models-inference/',
             },
               {
               label: 'Models-Management',
               to: '/api/models-management/',
             },
             {
               label: 'Skills',
               to: '/api/skills/',
             },
           ],
         },
            {
            type: 'doc',
            docId: 'versioning/changelog',
            position: 'left',
            label: 'Changelog',
          },
          {
            href: 'https://github.com/UKP-SQuARE/square-core/tree/master',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Overview',
                to: '/home/overview/introduction',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'Twitter',
                href: 'https://twitter.com/UKPLab',
              },
                {
                label: 'Linkedin',
                href: 'https://www.linkedin.com/company/tu-darmstadt/',
              },
            ],
          },
          {
            title: 'Legal',
            items: [
              {
                label: 'Terms',
                href: 'https://www.informatik.tu-darmstadt.de/ukp/impressum.en.jsp',
              },
              {
                label: 'Privacy Policy',
                href: 'https://www.tu-darmstadt.de/datenschutzerklaerung.en.jsp',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} UKP. All rights reserved.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
      },
    }),
};


module.exports = config;
