import React from "react";
import { 
  ShieldCheck, 
  Database, 
  AlertCircle, 
  ShieldAlert, 
  ArrowRight,
  TrendingUp
} from "lucide-react";
import type { DashboardSummary, Violation } from "../services/api";
import { SeverityBadge, StatusBadge } from "../components/common/Badges";

interface DashboardPageProps {
  summary: DashboardSummary | null;
  recentViolations: Violation[];
  onSelectViolation: (v: Violation) => void;
  onNavigate: (tab: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  summary,
  recentViolations,
  onSelectViolation,
  onNavigate,
}) => {
  if (!summary) {
    return (
      <div style={{ padding: 40, textAlign: "center", color: "var(--text-muted)" }}>
        Loading compliance telemetry...
      </div>
    );
  }

  const criticalCount = summary.severity_breakdown.find(s => s.severity === "CRITICAL")?.count || 0;
  const highCount = summary.severity_breakdown.find(s => s.severity === "HIGH")?.count || 0;
  const mediumCount = summary.severity_breakdown.find(s => s.severity === "MEDIUM")?.count || 0;
  const lowCount = summary.severity_breakdown.find(s => s.severity === "LOW")?.count || 0;

  const totalSev = criticalCount + highCount + mediumCount + lowCount || 1;
  const critPct = (criticalCount / totalSev) * 100;
  const highPct = (highCount / totalSev) * 100;
  const medPct = (mediumCount / totalSev) * 100;
  const lowPct = (lowCount / totalSev) * 100;

  return (
    <div>
      {/* KPI Cards Grid */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-header">
            <span>Compliance Health Rate</span>
            <ShieldCheck size={16} color="var(--status-resolved)" />
          </div>
          <div className="metric-value" style={{ 
            color: summary.compliance_score >= 90 ? "var(--status-resolved)" : "var(--severity-high)" 
          }}>
            {summary.compliance_score.toFixed(1)}%
          </div>
          <div className="metric-footer">
            <TrendingUp size={13} />
            <span>Target: &gt;95.0% adherence</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span>Audited Transactions</span>
            <Database size={16} color="var(--text-muted)" />
          </div>
          <div className="metric-value">{summary.total_records.toLocaleString()}</div>
          <div className="metric-footer">
            <span>Across {summary.total_datasets} batch ingestion files</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span>Open Violations</span>
            <AlertCircle size={16} color="var(--severity-high)" />
          </div>
          <div className="metric-value">{summary.open_violations}</div>
          <div className="metric-footer">
            <span>{summary.under_review_violations} under review</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span>Critical Flags</span>
            <ShieldAlert size={16} color="var(--severity-critical)" />
          </div>
          <div className="metric-value" style={{ color: criticalCount > 0 ? "var(--severity-critical)" : "var(--text-primary)" }}>
            {criticalCount}
          </div>
          <div className="metric-footer">
            <span>OFAC Sanctions &amp; Smurfing limits</span>
          </div>
        </div>
      </div>

      {/* Severity Breakdown & Telemetry Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 24 }}>
        {/* Severity Distribution */}
        <div className="section-card" style={{ margin: 0 }}>
          <div className="section-card-header">
            <div>
              <div className="section-title">Violation Severity Distribution</div>
              <div className="section-desc">Active deterministic policy breach weightings</div>
            </div>
          </div>
          <div style={{ padding: 18 }}>
            {/* Multi-segment progress bar */}
            <div style={{ 
              height: 10, 
              background: "var(--bg-surface-elevated)", 
              borderRadius: 4, 
              overflow: "hidden", 
              display: "flex",
              marginBottom: 16
            }}>
              <div style={{ width: `${critPct}%`, background: "var(--severity-critical)" }} title={`Critical: ${criticalCount}`} />
              <div style={{ width: `${highPct}%`, background: "var(--severity-high)" }} title={`High: ${highCount}`} />
              <div style={{ width: `${medPct}%`, background: "var(--severity-medium)" }} title={`Medium: ${mediumCount}`} />
              <div style={{ width: `${lowPct}%`, background: "var(--severity-low)" }} title={`Low: ${lowCount}`} />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12 }}>
                <span style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--severity-critical)" }} />
                <span style={{ color: "var(--text-muted)" }}>Critical:</span>
                <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>{criticalCount}</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12 }}>
                <span style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--severity-high)" }} />
                <span style={{ color: "var(--text-muted)" }}>High:</span>
                <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>{highCount}</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12 }}>
                <span style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--severity-medium)" }} />
                <span style={{ color: "var(--text-muted)" }}>Medium:</span>
                <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>{mediumCount}</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12 }}>
                <span style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--severity-low)" }} />
                <span style={{ color: "var(--text-muted)" }}>Low:</span>
                <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>{lowCount}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Top Breached Policies */}
        <div className="section-card" style={{ margin: 0 }}>
          <div className="section-card-header">
            <div>
              <div className="section-title">Rule Distribution Ranking</div>
              <div className="section-desc">Frequency by regulatory compliance code</div>
            </div>
            <button className="btn btn-outline btn-sm" onClick={() => onNavigate("rules")}>
              <span>View All</span>
            </button>
          </div>
          <div style={{ padding: "8px 18px" }}>
            {summary.rule_distribution.length === 0 ? (
              <div style={{ padding: "20px 0", color: "var(--text-muted)", fontSize: 12 }}>
                No violations flagged. System is fully compliant.
              </div>
            ) : (
              summary.rule_distribution.slice(0, 4).map((r) => (
                <div 
                  key={r.rule_code}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "8px 0",
                    borderBottom: "1px solid var(--border-subtle)",
                    fontSize: 12.5
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <code style={{ fontSize: 11, color: "var(--text-muted)" }}>{r.rule_code}</code>
                    <span style={{ color: "var(--text-primary)", fontWeight: 500 }}>{r.rule_name}</span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <SeverityBadge severity={r.severity} />
                    <span style={{ fontWeight: 600, color: "var(--text-primary)", minWidth: 20, textAlign: "right" }}>
                      {r.count}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Recent Violations Ledger Preview */}
      <div className="section-card">
        <div className="section-card-header">
          <div>
            <div className="section-title">Pending Violations Queue</div>
            <div className="section-desc">Immediate action required before regulatory filing deadline</div>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={() => onNavigate("violations")}>
            <span>View Full Ledger</span>
            <ArrowRight size={13} />
          </button>
        </div>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Transaction ID</th>
                <th>Rule Code</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Audit Finding</th>
                <th>Counterparty / Amount</th>
              </tr>
            </thead>
            <tbody>
              {recentViolations.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: "center", padding: 30, color: "var(--text-muted)" }}>
                    No pending violations in queue.
                  </td>
                </tr>
              ) : (
                recentViolations.slice(0, 5).map((v) => (
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
                    <td style={{ maxWidth: 300, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {v.message}
                    </td>
                    <td>
                      {v.record ? `${v.record.counterparty_name || "Direct"} ($${v.record.amount.toLocaleString()})` : "N/A"}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
