import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { App } from "../app/App";
import { createAppTestRouter } from "../app/router";

function renderApp(initialRoute = "/dashboard") {
  return render(<App router={createAppTestRouter([initialRoute])} />);
}

describe("App", () => {
  it("renders the dashboard route", () => {
    renderApp();

    expect(screen.getByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
    expect(screen.getByText(/operational summary shell/i)).toBeInTheDocument();
  });

  it("redirects from the root route to dashboard", () => {
    renderApp("/");

    expect(screen.getByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
  });

  it("navigates between shell routes", () => {
    renderApp();

    fireEvent.click(screen.getByRole("link", { name: /alerts/i }));

    expect(screen.getByRole("heading", { name: "Alerts" })).toBeInTheDocument();
  });
});
