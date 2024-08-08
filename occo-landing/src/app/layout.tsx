import Head from 'next/head';
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Navbar from '@/components/navbar/Navbar'
import Footer from '@/sections/footer/footer'
import { ToastContainer } from 'react-toastify'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  metadataBase: new URL('https://occo.landing.cydevaltd.com/'),
  title: 'Occo',
  description: 'MẠNG XÃ HỘI CỦA NGƯỜI VIỆT',
  openGraph: {
    type: 'website',
    url: 'https://occo.landing.cydevaltd.com/',
    title: 'Occo',
    description: 'MẠNG XÃ HỘI CỦA NGƯỜI VIỆT',
    siteName: 'Occo',
    images: [
      {
        url: 'https://occo.landing.cydevaltd.com/asset/images/logo.jpg',
        width: 800,
        height: 600,
        alt: 'Logo của Occo'
      }
    ]
  },
  // twitter: {
  //   card: 'summary_large_image',
  //   site: '@your_twitter_handle',
  //   creator: '@your_twitter_handle',
  //   title: 'Occo',
  //   description: 'MẠNG XÃ HỘI CỦA NGƯỜI VIỆT',
  //   image: 'https://occo.landing.cydevaltd.com/asset/images/logo.jpg'
  // }
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
        <link rel="icon" href="/favicon.ico" />
        <title>Occo</title>
      <body className={inter.className} style={{ backgroundColor: "#040623", minHeight: '100vh' }}>
        <Navbar />
        {children}
        <Footer />
        <ToastContainer />
      </body>
    </html>
  )
}
