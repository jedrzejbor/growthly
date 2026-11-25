import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <section className="route-page">
      <p className="eyebrow">404</p>
      <h1>Page not found</h1>
      <Button asChild>
        <Link href="/">Back to Growthly</Link>
      </Button>
    </section>
  );
}
