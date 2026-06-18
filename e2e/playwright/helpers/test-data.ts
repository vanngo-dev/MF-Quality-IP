export type AlertFixtureSeed = {
  equipmentId: number | null;
  stationId: number;
};

export function buildManufacturingAlertFixture({ equipmentId, stationId }: AlertFixtureSeed) {
  const suffix = `${Date.now()}-${Math.floor(Math.random() * 100_000)}`;

  return {
    alert_code: `E2E-AI-SUMMARY-${suffix}`,
    station_id: stationId,
    equipment_id: equipmentId,
    severity: "critical",
    title: `E2E torque quality alert ${suffix}`,
    description:
      "Automated E2E fixture for a torque quality issue with linked evidence for investigation summary generation.",
    evidence_json: {
      source: "playwright-e2e",
      metric_name: "torque_nm",
      observed_value: 52.4,
      upper_limit: 45,
      sample_count: 4,
      likely_area: "final torque station",
    },
    status: "open",
  };
}

export const investigationFixture = {
  title: "E2E investigation for torque quality alert",
  summary: "Reviewing repeated torque readings above the configured limit.",
  root_cause_hypothesis: "Possible tool calibration drift or fixture alignment issue.",
  status: "active",
};
