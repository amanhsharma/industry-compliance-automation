import React, { useState } from "react";
import { Shield, ArrowRight, AlertCircle } from "lucide-react";
import { api, type User } from "../services/api";

interface LoginPageProps {
  onLoginSuccess: (user: User) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("admin@meridian.com");
  const [password, setPassword] = useState("admin123");
  const [fullName, setFullName] = useState("");
  const [tenantName, setTenantName] = useState("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setLoading(true);

    try {
      if (isRegister) {
        if (!tenantName || !fullName) {
          setErrorMsg("Please fill in all tenant and personal details");
          setLoading(false);
          return;
        }
        const data = await api.register(tenantName, fullName, email, password);
        onLoginSuccess(data.user);
      } else {
        const data = await api.login(email, password);
        onLoginSuccess(data.user);
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  const setDemoCredentials = (role: "admin" | "officer") => {
    setIsRegister(false);
    setErrorMsg(null);
    if (role === "admin") {
      setEmail("admin@meridian.com");
      setPassword("admin123");
    } else {
      setEmail("compliance@meridian.com");
      setPassword("officer123");
    }
  };

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      backgroundColor: "var(--bg-app)",
      padding: 20
    }}>
      <div style={{
        width: 420,
        maxWidth: "100%",
        background: "var(--bg-surface)",
        border: "1px solid var(--border-subtle)",
        borderRadius: "var(--radius-lg)",
        boxShadow: "var(--shadow-lg)",
        padding: "32px 28px"
      }}>
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <div style={{
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            width: 42,
            height: 42,
            borderRadius: "var(--radius-md)",
            background: "var(--accent-primary)",
            color: "#fff",
            marginBottom: 12
          }}>
            <Shield size={22} />
          </div>
          <h2 style={{ fontSize: 18, fontWeight: 600, letterSpacing: -0.3, color: "var(--text-primary)" }}>
            Apex Compliance Engine
          </h2>
          <p style={{ fontSize: 12.5, color: "var(--text-muted)", marginTop: 4 }}>
            Multi-Tenant Regulatory Risk &amp; Ingestion Platform
          </p>
        </div>

        {/* Tab Switcher */}
        <div style={{
          display: "flex",
          borderBottom: "1px solid var(--border-subtle)",
          marginBottom: 20
        }}>
          <button
            type="button"
            style={{
              flex: 1,
              padding: "8px 0",
              background: "none",
              border: "none",
              borderBottom: !isRegister ? "2px solid var(--accent-primary)" : "2px solid transparent",
              color: !isRegister ? "var(--text-primary)" : "var(--text-muted)",
              fontWeight: 500,
              fontSize: 13,
              cursor: "pointer"
            }}
            onClick={() => { setIsRegister(false); setErrorMsg(null); }}
          >
            Sign In
          </button>
          <button
            type="button"
            style={{
              flex: 1,
              padding: "8px 0",
              background: "none",
              border: "none",
              borderBottom: isRegister ? "2px solid var(--accent-primary)" : "2px solid transparent",
              color: isRegister ? "var(--text-primary)" : "var(--text-muted)",
              fontWeight: 500,
              fontSize: 13,
              cursor: "pointer"
            }}
            onClick={() => { setIsRegister(true); setErrorMsg(null); }}
          >
            Create Organization
          </button>
        </div>

        {errorMsg && (
          <div style={{
            background: "var(--severity-critical-bg)",
            border: "1px solid var(--severity-critical-border)",
            color: "var(--severity-critical)",
            padding: "10px 12px",
            borderRadius: "var(--radius-sm)",
            fontSize: 12,
            marginBottom: 16,
            display: "flex",
            alignItems: "center",
            gap: 8
          }}>
            <AlertCircle size={15} />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {isRegister && (
            <>
              <div className="form-group">
                <label className="form-label">Company / Tenant Name</label>
                <input
                  type="text"
                  className="filter-input"
                  style={{ padding: "8px 12px" }}
                  placeholder="e.g. Apex Global Bank"
                  value={tenantName}
                  onChange={(e) => setTenantName(e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <input
                  type="text"
                  className="filter-input"
                  style={{ padding: "8px 12px" }}
                  placeholder="e.g. Elena Rostova"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                />
              </div>
            </>
          )}

          <div className="form-group">
            <label className="form-label">Work Email</label>
            <input
              type="email"
              className="filter-input"
              style={{ padding: "8px 12px" }}
              placeholder="officer@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group" style={{ marginBottom: 20 }}>
            <label className="form-label">Password</label>
            <input
              type="password"
              className="filter-input"
              style={{ padding: "8px 12px" }}
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: "100%", padding: "9px 0" }}
            disabled={loading}
          >
            <span>{loading ? "Authenticating..." : isRegister ? "Create Organization" : "Access Workspace"}</span>
            <ArrowRight size={14} />
          </button>
        </form>

        {/* Demo Fast Login Buttons */}
        {!isRegister && (
          <div style={{ marginTop: 24, paddingTop: 18, borderTop: "1px solid var(--border-subtle)" }}>
            <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600, marginBottom: 8, textAlign: "center" }}>
              Quick Demo Logins (Pre-Seeded)
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => setDemoCredentials("admin")}
              >
                <span>Lead Admin</span>
              </button>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => setDemoCredentials("officer")}
              >
                <span>Officer User</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
