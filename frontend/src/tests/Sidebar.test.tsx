import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { Sidebar } from "../components/layout/Sidebar";

describe("Sidebar", () => {
  it("renders all required navigation links", () => {
    render(
      <MemoryRouter initialEntries={["/dashboard"]}>
        <Sidebar />
      </MemoryRouter>,
    );

    for (const label of [
      "Dashboard",
      "Search",
      "Stations",
      "Equipment",
      "Vehicles",
      "Defects",
      "Alerts",
      "Investigations",
    ]) {
      expect(screen.getByRole("link", { name: new RegExp(label, "i") })).toBeInTheDocument();
    }
  });
});
