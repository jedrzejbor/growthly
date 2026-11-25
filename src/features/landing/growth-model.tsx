import { Layers3 } from "lucide-react";

export function GrowthModel() {
  return (
    <figure className="model-board">
      <figcaption>
        <Layers3 size={19} aria-hidden="true" /> The growth model
      </figcaption>
      <div className="model-art" aria-hidden="true">
        <div className="model-floor" />
        <div className="columns">
          {["one", "two", "three"].map((step) => (
            <div key={step} className={`column ${step}`}>
              <i />
              <b />
              <em />
            </div>
          ))}
        </div>
      </div>
      <ol className="model-legend" aria-label="How Growthly works">
        <li>Partner up</li>
        <li>Acquire customers</li>
        <li>Earn commission</li>
      </ol>
    </figure>
  );
}
