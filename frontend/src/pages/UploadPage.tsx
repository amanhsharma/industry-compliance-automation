import React, { useState, useRef } from "react";
import { UploadCloud, CheckCircle2, AlertCircle, FileSpreadsheet, Download, RefreshCw } from "lucide-react";
import { api, type Dataset } from "../services/api";

interface UploadPageProps {
  datasets: Dataset[];
  onUploadSuccess: () => void;
}

export const UploadPage: React.FC<UploadPageProps> = ({ datasets, onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successResult, setSuccessResult] = useState<{
    filename: string;
    rows: number;
    violations: number;
  } | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    if (!file.name.toLowerCase().endsWith(".csv")) {
      setErrorMsg("Invalid file format. Please upload a comma-separated values (.csv) file.");
      return;
    }

    setErrorMsg(null);
    setSuccessResult(null);
    setIsUploading(true);

    try {
      const res = await api.uploadCsv(file);
      setSuccessResult({
        filename: res.filename,
        rows: res.row_count,
        violations: res.violation_count,
      });
      onUploadSuccess();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to process CSV upload");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleDownloadSample = () => {
    const sampleCsvContent = `transaction_id,account_id,counterparty_name,counterparty_country,amount,currency,timestamp,kyc_status,transaction_type
TXN-2001,ACC-9901,Apex Global Trade,USA,12500.00,USD,2026-09-21T10:00:00Z,VERIFIED,WIRE_OUT
TXN-2002,ACC-9902,Tehran Petrochem,IRN,4200.00,USD,2026-09-21T10:15:00Z,VERIFIED,WIRE_OUT
TXN-2003,ACC-9903,Unverified Merchant,USA,2300.00,USD,2026-09-21T11:30:00Z,UNVERIFIED,ACH_OUT
TXN-2004,ACC-9904,Rapid Split Corp,CAN,9850.00,USD,2026-09-21T12:00:00Z,VERIFIED,WIRE_OUT
TXN-2005,ACC-9905,Standard Operations,USA,450.00,USD,2026-09-21T13:45:00Z,VERIFIED,ACH_OUT
TXN-2006,ACC-9906,Off-Hours Wire LLC,USA,8000.00,USD,2026-09-21T03:30:00Z,VERIFIED,WIRE_OUT`;

    const blob = new Blob([sampleCsvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "transactions_sample.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div>
      {/* Upload Box */}
      <div className="section-card">
        <div className="section-card-header">
          <div>
            <div className="section-title">Ingest Transaction Batch</div>
            <div className="section-desc">
              Upload CSV ledger for automated deterministic compliance evaluation &amp; sanctions screening
            </div>
          </div>
          <button className="btn btn-outline btn-sm" onClick={handleDownloadSample}>
            <Download size={13} />
            <span>Download Sample CSV</span>
          </button>
        </div>

        <div style={{ padding: 24 }}>
          {errorMsg && (
            <div style={{
              background: "var(--severity-critical-bg)",
              border: "1px solid var(--severity-critical-border)",
              color: "var(--severity-critical)",
              padding: "10px 14px",
              borderRadius: "var(--radius-sm)",
              marginBottom: 16,
              display: "flex",
              alignItems: "center",
              gap: 8,
              fontSize: 12.5
            }}>
              <AlertCircle size={16} />
              <span>{errorMsg}</span>
            </div>
          )}

          {successResult && (
            <div style={{
              background: "var(--status-resolved-bg)",
              border: "1px solid rgba(16, 185, 129, 0.3)",
              color: "var(--status-resolved)",
              padding: "12px 16px",
              borderRadius: "var(--radius-sm)",
              marginBottom: 16,
              display: "flex",
              alignItems: "center",
              gap: 10,
              fontSize: 12.5
            }}>
              <CheckCircle2 size={18} />
              <div>
                <b>Ingestion Completed:</b> Parsed <b>{successResult.rows}</b> records from <code>{successResult.filename}</code>.
                Detected <b>{successResult.violations}</b> compliance policy breaches.
              </div>
            </div>
          )}

          <div
            className={`dropzone ${isDragging ? "active" : ""}`}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              type="file"
              ref={fileInputRef}
              accept=".csv"
              style={{ display: "none" }}
              onChange={(e) => {
                if (e.target.files && e.target.files.length > 0) {
                  handleFile(e.target.files[0]);
                }
              }}
            />
            <UploadCloud size={36} color={isDragging ? "var(--accent-primary)" : "var(--text-muted)"} style={{ marginBottom: 10 }} />
            <div style={{ fontSize: 14, fontWeight: 500, color: "var(--text-primary)", marginBottom: 4 }}>
              {isUploading ? "Evaluating compliance policies against batch..." : "Drop transaction CSV here or browse"}
            </div>
            <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
              Supported columns: <code>transaction_id, account_id, amount, currency, counterparty_country, kyc_status, timestamp</code>
            </div>
          </div>
        </div>
      </div>

      {/* Dataset History */}
      <div className="section-card">
        <div className="section-card-header">
          <div>
            <div className="section-title">Batch Ingestion History</div>
            <div className="section-desc">Audited CSV files processed for this tenant</div>
          </div>
          <button className="btn btn-outline btn-sm" onClick={onUploadSuccess}>
            <RefreshCw size={13} />
            <span>Refresh</span>
          </button>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Batch Filename</th>
                <th>Status</th>
                <th>Records Ingested</th>
                <th>Violations Flagged</th>
                <th>File Size</th>
                <th>Ingestion Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {datasets.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: "center", padding: 30, color: "var(--text-muted)" }}>
                    No dataset batches uploaded yet.
                  </td>
                </tr>
              ) : (
                datasets.map((d) => (
                  <tr key={d.id}>
                    <td style={{ fontWeight: 500, color: "var(--text-primary)", display: "flex", alignItems: "center", gap: 8 }}>
                      <FileSpreadsheet size={15} color="var(--text-muted)" />
                      <span>{d.filename}</span>
                    </td>
                    <td>
                      <span className="badge badge-resolved">{d.status}</span>
                    </td>
                    <td>{d.row_count.toLocaleString()}</td>
                    <td style={{ fontWeight: 600, color: d.violation_count > 0 ? "var(--severity-high)" : "var(--status-resolved)" }}>
                      {d.violation_count}
                    </td>
                    <td>{(d.file_size_bytes / 1024).toFixed(1)} KB</td>
                    <td>{new Date(d.created_at).toLocaleString()}</td>
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
