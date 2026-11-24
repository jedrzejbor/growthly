import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { directories } from "./catalog";

export function Directory({ kind }: { kind: keyof typeof directories }) {
  const directory = directories[kind];
  return (
    <section className="route-page">
      <Link href="/" className="back-link">
        <ArrowLeft size={16} /> Home
      </Link>
      <p className="eyebrow">{directory.audience}</p>
      <h1>{directory.name}</h1>
      <p className="intro">{directory.description}</p>
      <div className="empty-state">
        <span className="icon-tile">
          <directory.icon size={24} />
        </span>
        <p>{directory.empty}</p>
      </div>
    </section>
  );
}
