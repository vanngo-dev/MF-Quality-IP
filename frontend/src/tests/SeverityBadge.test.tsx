import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { SeverityBadge, type SeverityValue } from "../components/ui/SeverityBadge";

describe("SeverityBadge", () => {
  it("renders supported severity labels", () => {
    const severities: SeverityValue[] = ["low", "medium", "high", "critical"];

    render(
      <>
        {severities.map((severity) => (
          <SeverityBadge key={severity} severity={severity} />
        ))}
      </>,
    );

    expect(screen.getByText("Low")).toBeInTheDocument();
    expect(screen.getByText("Medium")).toBeInTheDocument();
    expect(screen.getByText("High")).toBeInTheDocument();
    expect(screen.getByText("Critical")).toBeInTheDocument();
  });
});
