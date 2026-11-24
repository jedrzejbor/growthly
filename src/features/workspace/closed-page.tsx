import { redirect } from "next/navigation";

// Replace this closed entry point with server-side authorization before adding any data loaders.
export default function ClosedWorkspacePage(): never {
  redirect("/sign-in");
}
