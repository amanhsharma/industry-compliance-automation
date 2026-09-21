import React, { useState } from "react";
import { 
  Search, 
  X, 
  Check, 
  ArrowUpRight
} from "lucide-react";
import type { Violation } from "../services/api";
import { api } from "../services/api";
import { SeverityBadge, StatusBadge } from "../components/common/Badges";

interface ViolationsPageProps {
  violations: Violation[];
  selectedViolation: Violation | null;
  onSelectViolation: (v: Violation | null) => void;
  onViolationUpdated: () => void;
}

export const ViolationsPage: React.FC<ViolationsPageProps> = ({
  violations,
  selectedViolation,
  onSelectViolation,
  onViolationUpdated,
}) => {
  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");

  // Drawer edit state
  const [newStatus, setNewStatus] = useState<string>("");
  const [auditorNotes, setAuditorNotes] = useState<string>("");
  const [isSaving, setIsSaving] = useState(false);

  // Sync drawer state when selected violation changes
  React.useEffect(() => {
    if (selectedViolation) {
      setNewStatus(selectedViolation.status);
      setAuditorNotes(selectedViolation.auditor_notes || "");
    }
  }, [selectedViolation]);

  const filteredViolations = violations.filter((v) => {
    if (severityFilter !== "ALL" && v.severity !== severityFilter) return false;
    if (statusFilter !== "ALL" && v.status !== statusFilter) return false;
    if (search.trim()) {
      const q = search.toLowerCase();
      const txnMatch = v.record?.transaction_id?.toLowerCase().includes(q);
      const cpMatch = v.record?.counterparty_name?.toLowerCase().includes(q);
      const ruleMatch = v.rule_code.toLowerCase().includes(q) || v.rule_name.toLowerCase().includes(q);
      const msgMatch = v.message.toLowerCase().includes(q);
      if (!txnMatch && !cpMatch && !ruleMatch && !msgMatch) return false;
    }
    return true;
  });

  const handleSaveTriage = async () => {
    if (!selectedViolation) return;
    setIsSaving(true);
    try {
      await api.updateViolation(selectedViolation.id, {
        status: newStatus,
        auditor_notes: auditorNotes,
      });
      onViolationUpdated();
      onSelectViolation(null);
    } catch (err) {
      alert("Failed to save violation status update");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div>
      <div className="section-card">
        {/* Filter Bar */}
        <div className="filter-bar">
          <div className="filter-input-wrap">
            <Search />
            <input
              type="text"
              className="filter-input"
              placeholder="Search by Transaction ID, counterparty, rule or message..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
              Severity:
            </span>
            <select
              className="filter-select"
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
              Status:
            </span>
            <select
              className="filter-select"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="ALL">All Statuses</option>
              <option value="OPEN">Open</option>
              <option value="UNDER_REVIEW">Under Review</option>
              <option value="RESOLVED">Resolved</option>
            </select>
          </div>

          <div style={{ marginLeft: "auto", fontSize: 12, color: "var(--text-muted)" }}>
            Showing <b>{filteredViolations.length}</b> of {violations.length} findings
          </div>
        </div>

        {/* Violations Table */}
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Transaction</th>
                <th>Rule Code</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Violation Finding / Finding Detail</th>
                <th>Amount</th>
                <th>Country</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredViolations.length === 0 ? (
                <tr>
                  <td colSpan={8} style={{ textAlign: "center", padding: 36, color: "var(--text-muted)" }}>
                    No matching violations found with current filter criteria.
                  </td>
                </tr>
              ) : (
                filteredViolations.map((v) => (
                  <tr key={v.id} onClick={() => onSelectViolation(v)}>
                    <td style={{ fontWeight: 600, color: "var(--text-primary)" }}>
                      {v.record?.transaction_id || "TXN-N/A"}
                    </td>
                    <td>
                      <code style={{ fontSize: 11, color: "var(--text-muted)" }}>{v.rule_code}</code>
                    </td>
                    <td>
                      <SeverityBadge severity={v.severity} />
                    </td>
                    <td>
                      <StatusBadge status={v.status} />
                    </td>
                    <td style={{ maxWidth: 320, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {v.message}
                    </td>
                    <td>
                      {v.record ? `$${v.record.amount.toLocaleString()}` : "N/A"}
                    </td>
                    <td>
                      <span style={{ fontWeight: 600 }}>{v.record?.counterparty_country || "USA"}</span>
                    </td>
                    <td>
                      <button className="btn btn-secondary btn-sm" onClick={(e) => { e.stopPropagation(); onSelectViolation(v); }}>
                        <span>Triage</span>
                        <ArrowUpRight size={12} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Slide-over Inspection & Triage Drawer */}
      {selectedViolation && (
        <div className="drawer-backdrop" onClick={() => onSelectViolation(null)}>
          <div className="drawer-panel" onClick={(e) => e.stopPropagation()}>
            <div className="drawer-header">
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <SeverityBadge severity={selectedViolation.severity} />
                <span style={{ fontSize: 14, fontWeight: 600, color: "var(--text-primary)" }}>
                  Violation #{selectedViolation.record?.transaction_id || selectedViolation.id.slice(0, 8)}
                </span>
              </div>
              <button 
                className="btn btn-outline btn-sm" 
                style={{ padding: 4 }}
                onClick={() => onSelectViolation(null)}
              >
                <X size={16} />
              </button>
            </div>

            <div className="drawer-body">
              {/* Finding Box */}
              <div style={{
                background: "var(--bg-surface-elevated)",
                border: "1px solid var(--border-subtle)",
                borderRadius: "var(--radius-sm)",
                padding: 14,
                marginBottom: 20
              }}>
                <div style={{ fontSize: 11, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: 4 }}>
                  Rule: {selectedViolation.rule_code} — {selectedViolation.rule_name}
                </div>
                <div style={{ fontSize: 13, color: "var(--text-primary)", fontWeight: 500 }}>
                  {selectedViolation.message}
                </div>
              </div>

              {/* Transaction Metadata Ledger */}
              <div style={{ marginBottom: 20 }}>
                <div style={{ fontSize: 11.5, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: 10 }}>
                  Underlying Transaction Record
                </div>
                <div className="detail-list">
                  <div className="detail-row">
                    <span className="detail-key">Transaction ID:</span>
                    <span className="detail-val">{selectedViolation.record?.transaction_id || "N/A"}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-key">Originating Account:</span>
                    <span className="detail-val">{selectedViolation.record?.account_id || "N/A"}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-key">Amount &amp; Currency:</span>
                    <span className="detail-val" style={{ color: "var(--text-primary)", fontWeight: 600 }}>
                      ${selectedViolation.record?.amount.toLocaleString()} {selectedViolation.record?.currency || "USD"}
                    </span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-key">Counterparty:</span>
                    <span className="detail-val">{selectedViolation.record?.counterparty_name || "Direct Transfer"}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-key">Counterparty Country:</span>
                    <span className="detail-val" style={{ fontWeight: 600 }}>
                      {selectedViolation.record?.counterparty_country || "USA"}
                    </span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-key">Customer KYC Status:</span>
                    <span className="detail-val">
                      <span className={`badge ${selectedViolation.record?.kyc_status === "VERIFIED" ? "badge-resolved" : "badge-critical"}`}>
                        {selectedViolation.record?.kyc_status || "UNVERIFIED"}
                      </span>
                    </span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-key">Transfer Type:</span>
                    <span className="detail-val">{selectedViolation.record?.transaction_type || "WIRE_OUT"}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-key">Flagged At:</span>
                    <span className="detail-val">{new Date(selectedViolation.created_at).toLocaleString()}</span>
                  </div>
                </div>
              </div>

              {/* Triage Update Form */}
              <div>
                <div style={{ fontSize: 11.5, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: 12 }}>
                  Auditor Remediation &amp; Triage
                </div>

                <div className="form-group">
                  <label className="form-label">Workflow Status</label>
                  <select
                    className="filter-select"
                    style={{ width: "100%", padding: "8px 10px" }}
                    value={newStatus}
                    onChange={(e) => setNewStatus(e.target.value)}
                  >
                    <option value="OPEN">OPEN (Requires Investigation)</option>
                    <option value="UNDER_REVIEW">UNDER REVIEW (Escalated to Senior Officer)</option>
                    <option value="RESOLVED">RESOLVED (Remediation Attested)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Auditor Audit Trail Notes</label>
                  <textarea
                    className="form-textarea"
                    placeholder="Enter compliance rationale, SAR filing reference, or reason for resolution..."
                    value={auditorNotes}
                    onChange={(e) => setAuditorNotes(e.target.value)}
                  />
                </div>
              </div>
            </div>

            <div className="drawer-footer">
              <button className="btn btn-outline" onClick={() => onSelectViolation(null)}>
                Cancel
              </button>
              <button className="btn btn-primary" onClick={handleSaveTriage} disabled={isSaving}>
                <Check size={14} />
                <span>{isSaving ? "Saving..." : "Save Triage Changes"}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
