import { expect, test } from "@playwright/test";

for (const width of [320, 768]) {
  test(`landing fits ${width}px at a 32px default font and supports keyboard navigation`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height: 900 });
    const session = await page.context().newCDPSession(page);
    await session.send("Page.setFontSizes", { fontSizes: { standard: 32 } });
    await page.goto("/");
    await page.evaluate(() => document.fonts.ready);
    await expect(page.locator("html")).toHaveCSS("font-size", "32px");
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(
      width,
    );

    const legend = page.getByRole("list", { name: "How Growthly works" });
    const items = legend.getByRole("listitem");
    await expect(items).toHaveCount(3);
    // Measure rendered text lines: a clipped child can still have a visible bounding box.
    const fits = await items.evaluateAll((labels) =>
      labels.every((label) => {
        const box = label.closest("figure")!.getBoundingClientRect();
        const text = document.createRange();
        text.selectNodeContents(label);
        return Array.from(text.getClientRects()).every(
          (line) =>
            line.left >= box.left &&
            line.right <= box.right &&
            line.top >= box.top &&
            line.bottom <= box.bottom,
        );
      }),
    );
    expect(fits).toBe(true);

    await page.keyboard.press("Tab");
    const skip = page.getByRole("link", { name: "Skip to content" });
    await expect(skip).toBeFocused();
    await expect(skip).toBeInViewport();
    await page.keyboard.press("Enter");
    await expect(page).toHaveURL(/\/#main$/);
    await page.keyboard.press("Tab");
    await expect(page.getByRole("link", { name: "Explore campaigns", exact: true })).toBeFocused();

    await page.goto("/partners");
    await page.getByRole("banner").getByRole("link", { name: "Growthly home" }).focus();
    for (const name of ["Campaigns", "Partners", "Sign in"]) {
      await page.keyboard.press("Tab");
      const link = page.getByRole("navigation").getByRole("link", { name });
      await expect(link).toBeFocused();
      await expect(link).toBeInViewport({ ratio: 1 });
    }
    await page.keyboard.press("Enter");
    await expect(page.getByRole("heading", { name: "Sign in" })).toBeVisible();
  });
}
