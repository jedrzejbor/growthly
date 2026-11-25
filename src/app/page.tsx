import Link from "next/link";
import { ArrowRight, ArrowUpRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { GrowthModel } from "@/features/landing/growth-model";
import { directories } from "@/features/marketplace/catalog";

export default function Home() {
  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">
            <span className="accent-rule" />
            Performance marketplace
          </p>
          <h1>
            Partnerships
            <br />
            that drive <span>growth.</span>
          </h1>
          <p className="intro">
            Founders meet growth partners who bring in paying customers and earn commissions.
          </p>
          <div className="actions">
            <Button asChild>
              <Link href="/campaigns">
                Explore campaigns <ArrowRight size={17} />
              </Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/partners">Find a partner</Link>
            </Button>
          </div>
        </div>
        <GrowthModel />
      </section>
      <section className="discover" aria-labelledby="discover-title">
        <h2 id="discover-title">Explore the marketplace</h2>
        <div className="cards">
          {Object.values(directories).map((directory) => (
            <Link key={directory.href} href={directory.href} className="directory-card">
              <div className="card-top">
                <span className="icon-tile">
                  <directory.icon size={23} strokeWidth={1.7} />
                </span>
                <ArrowUpRight className="card-arrow" size={19} />
              </div>
              <p className="audience">{directory.audience}</p>
              <h3>{directory.name}</h3>
              <p>{directory.description}</p>
            </Link>
          ))}
        </div>
      </section>
    </>
  );
}
