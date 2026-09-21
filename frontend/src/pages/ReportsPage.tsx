import React, { useState } from "react";
import { CheckCircle2, ShieldAlert, FileText, DownloadCloud } from "lucide-react";
import { api, type DashboardSummary } from "../services/api";

interface ReportsPageProps {
  summary: DashboardSummary | null;
  tenantName: string;
}

export const ReportsPage: React.FC<ReportsPageProps> = ({ summary, tenantName }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [downloadSuccess, setDownloadSuccess] = useState(false);

  const handleDownloadPdf = async () => {
    setIsGenerating(true);
    setDownloadSuccess(false);
    try {
      const blob = await api.downloadReportPdf();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `compliance_audit_report_${tenantName.toLowerCase().replace(/\s+/g, "_")}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      setDownloadSuccess(true);
    } catch (err) {
      alert("Failed to download PDF report. Please ensure backend is running.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div>
      <div className="section-card">
        <div className="section-card-header">
          <div>
            <div className="section-title">Institutional Compliance Audit Report Generator</div>
            <div className="section-desc">
              Generate regulator-ready PDF audit summaries for BSA / AML / OFAC compliance exams
            </div>
          </div>
          <button 
            className="btn btn-primary"
            onClick={handleDownloadPdf}
            disabled={isGenerating}
          >
            <DownloadCloud size={15} />
            <span>{isGenerating ? "Compiling PDF Report..." : "Download Compliance PDF"}</span>
          </button>
        </div>

        <div style={{ padding: 24 }}>
          {downloadSuccess && (
            <div style={{
              background: "var(--status-resolved-bg)",
              border: "1px solid rgba(16, 185, 129, 0.3)",
              color: "var(--status-resolved)",
              padding: "12px 16px",
              borderRadius: "var(--radius-sm)",
              marginBottom: 20,
              display: "flex",
              alignItems: "center",
              gap: 10,
              fontSize: 12.5
            }}>
              <CheckCircle2 size={18} />
              <span>
                <b>Audit Report Downloaded Successfully:</b> The compiled PDF includes complete executive metrics, rule breach breakdowns, and auditor attestation signature lines.
              </span>
            </div>
          )}

          {/* Audit Parameters Manifest */}
          <div style={{
            background: "var(--bg-surface-elevated)",
            border: "1px solid var(--border-subtle)",
            borderRadius: "var(--radius-md)",
            padding: 20,
            marginBottom: 24
          }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)", marginBottom: 14 }}>
              Audit Report Parameters &amp; Scope
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16 }}>
              <div>
                <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase" }}>Legal Entity</div>
                <div style={{ fontSize: 14, fontWeight: 600, color: "var(--text-primary)", marginTop: 2 }}>
                  {tenantName || "Meridian Financial Services"}
                </div>
              </div>

              <div>
                <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase" }}>Regulatory Scope</div>
                <div style={{ fontSize: 14, fontWeight: 600, color: "var(--text-primary)", marginTop: 2 }}>
                  BSA / AML / OFAC / FinCEN CDD
                </div>
              </div>

              <div>
                <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase" }}>Compliance Adherence</div>
                <div style={{ fontSize: 14, fontWeight: 600, color: "var(--status-resolved)", marginTop: 2 }}>
                  {summary?.compliance_score.toFixed(1) || 100.0}% Score
                </div>
              </div>

              <div>
                <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase" }}>Total Flagged Findings</div>
                <div style={{ fontSize: 14, fontWeight: 600, color: "var(--severity-high)", marginTop: 2 }}>
                  {summary?.total_violations || 0} Findings
                </div>
              </div>
            </div>
          </div>

          {/* Report Sections Breakdown Card */}
          <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)", marginBottom: 12 }}>
            Included Document Sections
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 14 }}>
            <div style={{
              background: "var(--bg-surface)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "var(--radius-sm)",
              padding: 16
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                <FileText size={16} color="var(--accent-primary)" />
                <span style={{ fontWeight: 600, fontSize: 13, color: "var(--text-primary)" }}>1. Executive Summary</span>
              </div>
              <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
                Aggregated compliance health score, total transactions audited, and breakdown of findings by Critical and High severity levels.
              </div>
            </div>

            <div style={{
              background: "var(--bg-surface)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "var(--radius-sm)",
              padding: 16
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                <ShieldAlert size={16} color="var(--severity-high)" />
                <span style={{ fontWeight: 600, fontSize: 13, color: "var(--text-primary)" }}>2. Policy Breaches Ledger</span>
              </div>
              <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
                Itemized findings cross-referenced with rule codes, sanctions screening results, counterparty jurisdictions, and audit findings.
              </div>
            </div>

            <div style={{
              background: "var(--bg-surface)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "var(--radius-sm)",
              padding: 16
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                <CheckCircle2 size={16} color="var(--status-resolved)" />
                <span style={{ fontWeight: 600, fontSize: 13, color: "var(--text-primary)" }}>3. Auditor Attestation</span>
              </div>
              <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
                Official sign-off blocks, compliance officer affirmation lines, and regulatory exam filing metadata.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
