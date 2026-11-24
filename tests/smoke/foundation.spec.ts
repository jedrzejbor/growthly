import { expect, test } from "@playwright/test";

test("home links to both public marketplaces", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toContainText("that drive growth.");
  await expect(page.getByRole("figure")).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.getByRole("link", { name: "Explore campaigns", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Campaign marketplace" })).toBeVisible();
  await expect(page.getByText("No campaigns are listed yet.")).toBeVisible();
  await page.getByRole("navigation").getByRole("link", { name: "Partners" }).click();
  await expect(page.getByRole("heading", { name: "Partner marketplace" })).toBeVisible();
  await expect(page.getByText("No growth partners are listed yet.")).toBeVisible();
});

test("sign-in is informational", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "Sign in" }).click();
  await expect(page.getByRole("heading", { name: "Sign in" })).toBeVisible();
  await expect(page.locator("input")).toHaveCount(0);
});

for (const path of [
  "/dashboard/founder",
  "/dashboard/partner",
  "/dashboard/admin",
  "/collaborations",
  "/referrals",
  "/payments",
  "/commissions",
]) {
  test(`${path} redirects before serving workspace content`, async ({ request }) => {
    const response = await request.get(path, { maxRedirects: 0 });
    expect(response.status()).toBe(307);
    expect(new URL(response.headers().location!, response.url()).pathname).toBe("/sign-in");
  });
}

test("unknown routes return 404", async ({ page }) => {
  const response = await page.goto("/unknown-foundation-route");
  expect(response?.status()).toBe(404);
  await expect(page.getByRole("heading", { name: "Page not found" })).toBeVisible();
});
