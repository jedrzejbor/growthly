import { Directory } from "@/features/marketplace/directory";
import { directories } from "@/features/marketplace/catalog";

export const metadata = { title: directories.partners.name };

export default function Page() {
  return <Directory kind="partners" />;
}
