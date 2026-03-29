import type { Metadata } from "next";
import "./globals.css";
import { Bricolage_Grotesque, Manrope } from "next/font/google";

const display = Bricolage_Grotesque({
  subsets: ["latin"],
  weight: ["400", "600", "700", "800"],
  variable: "--font-display"
});

const body = Manrope({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-body"
});

export const metadata: Metadata = {
  title: "Mobile OTP",
  description: "Mobile number and OTP verification screens"
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${body.variable} ${display.variable}`}>
        <div className="ambient" aria-hidden="true">
          <span className="orb one" />
          <span className="orb two" />
        </div>
        {children}
      </body>
    </html>
  );
}