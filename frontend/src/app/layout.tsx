import type { Metadata } from 'next';
import React from 'react';
import './globals.css';

export const metadata: Metadata = {
  title: 'Global Gold Market Intelligence & Prediction Terminal',
  description: 'Editorial financial intelligence platform with regime classification, conformal uncertainty, and multi-horizon price forecasting.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-[#F5F1E8] text-[#343A36] antialiased min-h-screen selection:bg-[#B08D45] selection:text-white">
        {children}
      </body>
    </html>
  );
}
