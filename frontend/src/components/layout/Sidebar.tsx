import {
  AlertTriangle,
  ClipboardList,
  Gauge,
  MapPin,
  SearchCheck,
  Search,
  Settings,
  Truck,
} from "lucide-react";
import { NavLink } from "react-router-dom";

const navigationItems = [
  { to: "/dashboard", label: "Dashboard", icon: Gauge },
  { to: "/search", label: "Search", icon: Search },
  { to: "/stations", label: "Stations", icon: MapPin },
  { to: "/equipment", label: "Equipment", icon: Settings },
  { to: "/vehicles", label: "Vehicles", icon: Truck },
  { to: "/defects", label: "Defects", icon: AlertTriangle },
  { to: "/alerts", label: "Alerts", icon: SearchCheck },
  { to: "/investigations", label: "Investigations", icon: ClipboardList },
];

export function Sidebar() {
  return (
    <aside className="sidebar" aria-label="Primary navigation">
      <div className="sidebar-brand">
        <span className="brand-mark" aria-hidden="true">
          MQ
        </span>
        <div>
          <strong>Quality IP</strong>
          <span>Manufacturing intelligence</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navigationItems.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              className={({ isActive }) => `nav-link${isActive ? " is-active" : ""}`}
              key={item.to}
              to={item.to}
            >
              <Icon aria-hidden="true" size={18} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}
