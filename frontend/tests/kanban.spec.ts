import { expect, test } from "@playwright/test";
import { initialData } from "../src/lib/kanban";

const API = "http://127.0.0.1:8000";

const seedBoard = async (request) => {
  await request.post(`${API}/api/board`, {
    data: { board: initialData },
  });
};

const login = async (page) => {
  await page.goto("/");
  await page.getByLabel("Username").fill("user");
  await page.getByLabel("Password").fill("password");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
};

test.beforeEach(async ({ request }) => {
  await seedBoard(request);
});

test("loads the kanban board", async ({ page }) => {
  await login(page);
  await expect(page.locator('[data-testid^="column-"]')).toHaveCount(5);
});

test("adds a card to a column", async ({ page }) => {
  await login(page);
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  await firstColumn.getByRole("button", { name: /add a card/i }).click();
  await firstColumn.getByPlaceholder("Card title").fill("Playwright card");
  await firstColumn.getByPlaceholder("Details").fill("Added via e2e.");
  await firstColumn.getByRole("button", { name: /add card/i }).click();
  await expect(firstColumn.getByText("Playwright card")).toBeVisible();
});

test("board state persists after reload", async ({ page }) => {
  await login(page);
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  await firstColumn.getByRole("button", { name: /add a card/i }).click();
  await firstColumn.getByPlaceholder("Card title").fill("Persistent card");
  await firstColumn.getByPlaceholder("Details").fill("Should survive reload.");
  await firstColumn.getByRole("button", { name: /add card/i }).click();
  await expect(firstColumn.getByText("Persistent card")).toBeVisible();

  // Wait for the save request to complete before reloading
  await page.waitForLoadState("networkidle");
  await page.reload();
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  await expect(page.locator('[data-testid^="column-"]').first().getByText("Persistent card")).toBeVisible();
});

test("moves a card between columns", async ({ page }) => {
  await login(page);
  await page.waitForLoadState("networkidle");
  const card = page.getByTestId("card-card-1");
  await expect(card).toBeVisible();
  const targetColumn = page.getByTestId("column-col-review");
  const cardBox = await card.boundingBox();
  const columnBox = await targetColumn.boundingBox();
  if (!cardBox || !columnBox) {
    throw new Error("Unable to resolve drag coordinates.");
  }

  // Use pointer events with slow movement so @dnd-kit recognises the drag
  await page.mouse.move(cardBox.x + cardBox.width / 2, cardBox.y + cardBox.height / 2);
  await page.mouse.down();
  await page.mouse.move(cardBox.x + cardBox.width / 2 + 10, cardBox.y + cardBox.height / 2, { steps: 5 });
  await page.mouse.move(columnBox.x + columnBox.width / 2, columnBox.y + 150, { steps: 30 });
  await page.waitForTimeout(100);
  await page.mouse.up();
  await expect(targetColumn.getByTestId("card-card-1")).toBeVisible();
});

test("smokes backend /api/board endpoint", async ({ request }) => {
  const response = await request.get(`${API}/api/board`);
  expect(response.ok()).toBeTruthy();

  const body = await response.json();
  expect(body.userId).toBe("user");
  expect(body.board).toBeDefined();
  expect(Array.isArray(body.board.columns)).toBe(true);
  expect(body.board.cards).toBeDefined();
  expect(typeof body.updatedAt).toBe("string");
});
