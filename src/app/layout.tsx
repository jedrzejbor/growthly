import type { Metadata } from "next";
import type { ReactNode } from "react";
import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import "@fontsource-variable/dm-sans/wght.css";
import "./globals.css";
import { Brand } from "@/components/brand";

export const metadata: Metadata = {
  title: { default: "Growthly | Performance partnerships", template: "%s | Growthly" },
  description: "A performance-based marketplace connecting founders and growth partners.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <a href="#main" className="skip-link">
          Skip to content
        </a>
        <header className="masthead">
          <div className="frame nav-row">
            <Brand />
            <nav aria-label="Main navigation" className="nav-links">
              <Link href="/campaigns">Campaigns</Link>
              <Link href="/partners">Partners</Link>
              <Link className="sign-in" href="/sign-in">
                Sign in <ArrowUpRight size={15} aria-hidden="true" />
              </Link>
            </nav>
          </div>
        </header>
        <main id="main" className="frame">
          {children}
        </main>
        <footer className="frame footer">
          <Brand />
          <span>Performance partnerships</span>
        </footer>
      </body>
    </html>
  );
}
