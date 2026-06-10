import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";

const healthResponse = {
  status: "ok",
  service: "manufacturing-quality-api",
  environment: "local",
  dependencies: {
    postgres: "configured",
    redpanda: "configured",
    elasticsearch: "configured",
    ai_provider: "mock",
  },
};

describe("App", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.clearAllMocks();
  });

  it("renders the backend health contract", async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: async () => healthResponse,
    } as Response);

    render(<App />);

    expect(screen.getByRole("heading", { name: /quality operations/i })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("manufacturing-quality-api")).toBeInTheDocument();
    });

    expect(screen.getByText("PostgreSQL")).toBeInTheDocument();
    expect(screen.getByText("Redpanda")).toBeInTheDocument();
    expect(screen.getByText("Elasticsearch")).toBeInTheDocument();
    expect(screen.getByText("mock")).toBeInTheDocument();
  });

  it("shows an unavailable status when the API cannot be reached", async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error("offline"));

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Unavailable")).toBeInTheDocument();
    });

    expect(screen.getByText("Backend health endpoint is not responding.")).toBeInTheDocument();
  });
});
