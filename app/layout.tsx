import type { Metadata } from "next";
import { Geist } from 'next/font/google';
// Ensure the import path and named export are correct
import { AuthProvider } from '../contexts/AuthContext';
import "./globals.css";

const geist = Geist({
  subsets: ['latin'],
  display: 'swap',
});

export const metadata: Metadata = {
  title: "DR Detection System",
  description: "Automated Diabetic Retinopathy Detection using AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={geist.className}>
      <body className="min-h-screen bg-gray-50">
        <AuthProvider>
          <main className="container mx-auto px-4 py-8">
            {children}
          </main>
        </AuthProvider>
      </body>
    </html>
  );
}

