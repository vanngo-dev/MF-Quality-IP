import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { App } from "../app/App";
import { createAppTestRouter } from "../app/router";
import { mockApiResponses } from "./testUtils";

function renderApp(initialRoute = "/dashboard") {
  return render(<App router={createAppTestRouter([initialRoute])} />);
}

describe("App", () => {
  it("renders the dashboard route", async () => {
    mockApiResponses();

    renderApp();

    expect(await screen.findByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
    expect(screen.getByText(/live manufacturing quality summary/i)).toBeInTheDocument();
  });

  it("redirects from the root route to dashboard", async () => {
    mockApiResponses();

    renderApp("/");

    expect(await screen.findByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
  });

  it("navigates between shell routes", async () => {
    mockApiResponses();

    renderApp();

    expect(await screen.findByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("link", { name: /alerts/i }));

    expect(await screen.findByRole("heading", { name: "Alerts" })).toBeInTheDocument();
  });
});
