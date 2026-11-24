import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

export const metadata = { title: "Sign in" };

export default function SignIn() {
  return (
    <section className="route-page">
      <p className="eyebrow">Workspace access</p>
      <h1>Sign in</h1>
      <p className="intro">
        Workspace access is in development. The public marketplaces are open to explore.
      </p>
      <Button asChild>
        <Link href="/campaigns">
          Explore campaigns <ArrowRight size={17} />
        </Link>
      </Button>
    </section>
  );
}
