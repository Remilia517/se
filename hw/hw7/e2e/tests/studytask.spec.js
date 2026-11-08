const { test, expect } = require("@playwright/test");

test("首頁顯示 API 與資料庫連線狀態", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#health")).toContainText("系統正常");
});

test("使用者可以新增、完成並刪除作業", async ({ page }) => {
  const title = `E2E 自動化測試 ${Date.now()}`;
  await page.goto("/");

  await page.locator("#title").fill(title);
  await page.locator("#course").fill("軟體工程");
  await page.locator("#form button[type=submit]").click();

  const task = page.locator(".task").filter({ hasText: title });
  await expect(task).toBeVisible();

  await task.locator('input[type="checkbox"]').check();
  await expect(task).toHaveClass(/done/);

  await page.evaluate(() => {
    window.confirm = () => true;
  });
  await task.getByRole("button", { name: "刪除" }).click();
  await expect(page.locator(".task").filter({ hasText: title })).toHaveCount(0);
});
