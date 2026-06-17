import { Navigate, createBrowserRouter, createMemoryRouter } from "react-router-dom";

import { AppLayout } from "../components/layout/AppLayout";
import { AlertDetailPage } from "../features/alerts/AlertDetailPage";
import { AlertsPage } from "../features/alerts/AlertsPage";
import { DashboardPage } from "../features/dashboard/DashboardPage";
import { DefectsPage } from "../features/defects/DefectsPage";
import { EquipmentPage } from "../features/equipment/EquipmentPage";
import { InvestigationDetailPage } from "../features/investigations/InvestigationDetailPage";
import { InvestigationsPage } from "../features/investigations/InvestigationsPage";
import { SearchPage } from "../features/search/SearchPage";
import { StationsPage } from "../features/stations/StationsPage";
import { VehiclesPage } from "../features/vehicles/VehiclesPage";

export const routes = [
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: "dashboard", element: <DashboardPage /> },
      { path: "search", element: <SearchPage /> },
      { path: "stations", element: <StationsPage /> },
      { path: "equipment", element: <EquipmentPage /> },
      { path: "vehicles", element: <VehiclesPage /> },
      { path: "defects", element: <DefectsPage /> },
      { path: "alerts", element: <AlertsPage /> },
      { path: "alerts/:alertId", element: <AlertDetailPage /> },
      { path: "investigations", element: <InvestigationsPage /> },
      { path: "investigations/:investigationId", element: <InvestigationDetailPage /> },
      { path: "*", element: <Navigate to="/dashboard" replace /> },
    ],
  },
];

export function createAppRouter() {
  return createBrowserRouter(routes);
}

export function createAppTestRouter(initialEntries: string[] = ["/dashboard"]) {
  return createMemoryRouter(routes, { initialEntries });
}
