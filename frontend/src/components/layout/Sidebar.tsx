import React from "react";
import { 
  LayoutDashboard, 
  UploadCloud, 
  AlertTriangle, 
  FileText, 
  ShieldCheck, 
  LogOut 
} from "lucide-react";
import type { User } from "../../services/api";

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  user: User | null;
  openViolationsCount: number;
  onLogout: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  setCurrentTab,
  user,
  openViolationsCount,
  onLogout,
}) => {
  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "upload", label: "Ingestion & Upload", icon: UploadCloud },
    { 
      id: "violations", 
      label: "Violations Triage", 
      icon: AlertTriangle, 
      count: openViolationsCount,
      alert: openViolationsCount > 0 
    },
    { id: "reports", label: "Audit Reports (PDF)", icon: FileText },
    { id: "rules", label: "Rules Repository", icon: ShieldCheck },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand-badge">A</div>
        <div className="brand-title">APEX COMPLIANCE</div>
        <div className="brand-env">V1.0</div>
      </div>

      <div className="tenant-selector">
        <div className="tenant-pill">
          <div className="tenant-name">{user?.tenant?.name || "Meridian Financial"}</div>
          <span style={{ fontSize: 10, color: "var(--text-muted)" }}>TENANT</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section-title">Operations</div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? "active" : ""}`}
              onClick={() => setCurrentTab(item.id)}
            >
              <Icon />
              <span>{item.label}</span>
              {item.count !== undefined && item.count > 0 && (
                <span className={`nav-counter ${item.alert ? "alert" : ""}`}>
                  {item.count}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="user-avatar">
          {user?.full_name ? user.full_name.charAt(0).toUpperCase() : "U"}
        </div>
        <div className="user-info">
          <div className="user-name">{user?.full_name || "Auditor"}</div>
          <div className="user-role">{user?.role?.replace("_", " ") || "Officer"}</div>
        </div>
        <button className="logout-btn" title="Sign out" onClick={onLogout}>
          <LogOut size={16} />
        </button>
      </div>
    </aside>
  );
};
