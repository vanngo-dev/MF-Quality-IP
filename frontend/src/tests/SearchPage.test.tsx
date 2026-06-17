import { fireEvent, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { SearchPage } from "../features/search/SearchPage";
import { mockApiFailure, mockApiResponses, renderWithQueryClient } from "./testUtils";

describe("SearchPage", () => {
  it("renders the search page", () => {
    renderWithQueryClient(<SearchPage />);

    expect(screen.getByRole("heading", { name: "Search" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Search" })).toBeInTheDocument();
  });

  it("accepts text in the search input", () => {
    renderWithQueryClient(<SearchPage />);

    fireEvent.change(screen.getByLabelText("Query"), { target: { value: "torque" } });

    expect(screen.getByDisplayValue("torque")).toBeInTheDocument();
  });

  it("submitting search calls the API client", async () => {
    const fetchMock = mockApiResponses();

    renderWithQueryClient(<SearchPage />);

    fireEvent.change(screen.getByLabelText("Query"), { target: { value: "torque" } });
    fireEvent.click(screen.getByRole("button", { name: "Search" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "http://localhost:8000/api/v1/search?q=torque",
        expect.any(Object),
      );
    });
  });

  it("shows a loading state while search is pending", async () => {
    vi.stubGlobal("fetch", vi.fn(() => new Promise<Response>(() => undefined)));

    renderWithQueryClient(<SearchPage />);

    fireEvent.change(screen.getByLabelText("Query"), { target: { value: "torque" } });
    fireEvent.click(screen.getByRole("button", { name: "Search" }));

    expect(await screen.findByText("Searching quality records...")).toBeInTheDocument();
  });

  it("shows an error state when search fails", async () => {
    mockApiFailure();

    renderWithQueryClient(<SearchPage />);

    fireEvent.change(screen.getByLabelText("Query"), { target: { value: "torque" } });
    fireEvent.click(screen.getByRole("button", { name: "Search" }));

    expect(await screen.findByText("Unable to search quality records.")).toBeInTheDocument();
  });

  it("renders grouped search results", async () => {
    mockApiResponses();

    renderWithQueryClient(<SearchPage />);

    fireEvent.change(screen.getByLabelText("Query"), { target: { value: "torque" } });
    fireEvent.click(screen.getByRole("button", { name: "Search" }));

    expect(await screen.findByText("TORQUE_LOW")).toBeInTheDocument();
    expect(screen.getByText("Repeated torque defects")).toBeInTheDocument();
    expect(screen.getByText("Investigate repeated torque defects")).toBeInTheDocument();
    expect(screen.getByText("station_exit")).toBeInTheDocument();
  });

  it("renders a no results message", async () => {
    mockApiResponses({
      "GET /api/v1/search": {
        query: "nonsense",
        results: {
          defects: [],
          alerts: [],
          investigations: [],
          events: [],
        },
      },
    });

    renderWithQueryClient(<SearchPage />);

    fireEvent.change(screen.getByLabelText("Query"), { target: { value: "nonsense" } });
    fireEvent.click(screen.getByRole("button", { name: "Search" }));

    expect(await screen.findByText("No results found.")).toBeInTheDocument();
  });
});

