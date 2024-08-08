import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/sections/**/*.{js,ts,jsx,tsx,mdx}',

  ],
  reactStrictMode: false,

  theme: {
    extend: {
      backgroundImage: {
       
      },
      linearColors: {
       
        'custom-blue': ['#770DD5', '#C10CD1'],
      },
      colors: {
        customBlack: '#040623',
        navCor:"#230D48",
        customText:"#817DA0",
        purpleCus:"#770DD5",
        paleteCus:"#C10CD1",
        customGrey:"#817DA0",
        purple_cus:"#6A0F83",
        blue_pur:"#470D79",
        customPurple:"#A11BC7",
        linear_nav_a:"#EC5DF8",
        linear_nav_b:"#AA4ABA",
        linear_nav_c:"#D568D1",
        p_1:"#6603AC",
        p_2:"#EF01BC"

      },  
    },
  },
  plugins: [ require('daisyui'),],
}
export default config
