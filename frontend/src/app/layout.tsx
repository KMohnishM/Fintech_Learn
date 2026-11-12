import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Global Trade Finance & UCP 600 Workbench",
  description: "Enterprise Trade Finance Letter of Credit Discrepancy Engine",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
