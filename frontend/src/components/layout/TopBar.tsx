import React from "react";
import { UploadCloud, FileDown } from "lucide-react";

interface TopBarProps {
  currentTab: string;
  onQuickUpload: () => void;
  onQuickReport: () => void;
}

export const TopBar: React.FC<TopBarProps> = ({ currentTab, onQuickUpload, onQuickReport }) => {
  const titles: Record<string, string> = {
    dashboard: "Compliance Executive Overview",
    upload: "Transaction Ingestion & Batch Processing",
    violations: "Violations Ledger & Triage Desk",
    reports: "Audit Reports & Regulatory Filing",
    rules: "Deterministic Rules Engine Policies",
  };

  return (
    <header className="topbar">
      <div className="topbar-left">
        <h1 className="page-title">{titles[currentTab] || "Compliance Dashboard"}</h1>
      </div>
      <div className="topbar-right">
        <button className="btn btn-secondary btn-sm" onClick={onQuickUpload}>
          <UploadCloud size={14} />
          <span>Ingest CSV</span>
        </button>
        <button className="btn btn-primary btn-sm" onClick={onQuickReport}>
          <FileDown size={14} />
          <span>Generate PDF</span>
        </button>
      </div>
    </header>
  );
};
