import { Directory } from "@/features/marketplace/directory";
import { directories } from "@/features/marketplace/catalog";

export const metadata = { title: directories.campaigns.name };

export default function Page() {
  return <Directory kind="campaigns" />;
}
