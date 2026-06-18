import { expect, test } from "@playwright/test";

import { createAlertFixture, expectBackendHealthy } from "./helpers/api";
import { investigationFixture } from "./helpers/test-data";

const apiUrl = process.env.E2E_API_URL ?? "http://localhost:8000";

test.describe("manufacturing quality workflow", () => {
  test("creates, summarizes, and resolves an investigation from an alert", async ({ page, request }) => {
    await expectBackendHealthy(request, apiUrl);
    const alert = await createAlertFixture(request, apiUrl);

    await page.goto("/");
    await expect(page.getByTestId("dashboard-page")).toBeVisible();

    await page.getByRole("link", { name: "Alerts" }).click();
    await expect(page.getByTestId("alerts-page")).toBeVisible();
    await expect(page.getByText(alert.title)).toBeVisible();
    await expect(page.getByTestId("alert-row").first()).toBeVisible();

    await page.getByRole("link", { name: alert.title }).click();
    await expect(page.getByTestId("alert-detail-page")).toBeVisible();
    await expect(page.getByText(alert.alert_code)).toBeVisible();

    await page.getByTestId("create-investigation-button").click();
    const form = page.getByTestId("investigation-form");
    await expect(form).toBeVisible();
    await form.getByLabel("Title").fill(investigationFixture.title);
    await form.getByLabel("Summary").fill(investigationFixture.summary);
    await form.getByLabel("Root-cause hypothesis").fill(investigationFixture.root_cause_hypothesis);
    await form.getByTestId("investigation-status-select").selectOption(investigationFixture.status);
    await form.getByTestId("save-investigation-button").click();

    await expect(page.getByTestId("investigation-detail-page")).toBeVisible();
    await expect(page.getByTestId("investigation-detail-page")).toContainText(investigationFixture.title);

    await page.getByTestId("generate-ai-summary-button").click();
    const summaryPanel = page.getByTestId("ai-summary-panel");
    await expect(summaryPanel).toContainText("Likely Issue");
    await expect(summaryPanel).toContainText("Evidence");
    await expect(summaryPanel).toContainText("Recommended Next Checks");
    await expect(summaryPanel).toContainText(/low|medium|high/i);
    await expect(summaryPanel).toContainText("Limitations");

    await page.getByTestId("resolve-investigation-button").click();
    await expect(page.getByTestId("investigation-detail-page")).toContainText("Resolved");
  });
});
