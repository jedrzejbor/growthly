import { Megaphone, UsersRound } from "lucide-react";

export const directories = {
  campaigns: {
    href: "/campaigns",
    name: "Campaign marketplace",
    audience: "For growth partners",
    description: "Explore opportunities to bring paying customers to founders.",
    empty: "No campaigns are listed yet.",
    icon: Megaphone,
  },
  partners: {
    href: "/partners",
    name: "Partner marketplace",
    audience: "For founders",
    description: "Discover growth partners who can help you acquire customers.",
    empty: "No growth partners are listed yet.",
    icon: UsersRound,
  },
} as const;
