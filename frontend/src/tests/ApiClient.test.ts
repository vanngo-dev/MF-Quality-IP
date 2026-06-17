import { describe, expect, it } from "vitest";

import { DEFAULT_API_BASE_URL, getApiBaseUrl } from "../services/apiClient";

describe("apiClient", () => {
  it("uses the configured base URL or default base URL", () => {
    expect(getApiBaseUrl()).toBe(DEFAULT_API_BASE_URL);
  });
});
