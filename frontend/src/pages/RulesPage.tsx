import React, { useState } from "react";
import { ToggleLeft, ToggleRight } from "lucide-react";
import { api, type ComplianceRule } from "../services/api";
import { SeverityBadge } from "../components/common/Badges";

interface RulesPageProps {
  rules: ComplianceRule[];
  isAdmin: boolean;
  onRuleToggled: () => void;
}

export const RulesPage: React.FC<RulesPageProps> = ({ rules, isAdmin, onRuleToggled }) => {
  const [togglingId, setTogglingId] = useState<string | null>(null);

  const handleToggle = async (rule: ComplianceRule) => {
    if (!isAdmin) {
      alert("Only Admins can modify compliance rule configurations.");
      return;
    }
    setTogglingId(rule.id);
    try {
      await api.toggleRule(rule.id, !rule.is_active);
      onRuleToggled();
    } catch (err) {
      alert("Failed to toggle rule state");
    } finally {
      setTogglingId(null);
    }
  };

  return (
    <div>
      <div className="section-card">
        <div className="section-card-header">
          <div>
            <div className="section-title">Deterministic Compliance Rules Engine</div>
            <div className="section-desc">
              Active statutory policies and quantitative thresholds enforced across transaction batches
            </div>
          </div>
          <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
            Framework: <b>BSA / AML / OFAC Single-Country V1</b>
          </div>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Rule Code</th>
                <th>Policy Name &amp; Framework</th>
                <th>Category</th>
                <th>Severity</th>
                <th>Deterministic Parameters</th>
                <th>State</th>
              </tr>
            </thead>
            <tbody>
              {rules.map((rule) => {
                let params = {};
                try {
                  params = JSON.parse(rule.parameters_json);
                } catch (e) {
                  params = {};
                }

                return (
                  <tr key={rule.id}>
                    <td style={{ fontWeight: 600, color: "var(--text-primary)" }}>
                      <code>{rule.code}</code>
                    </td>
                    <td>
                      <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>{rule.name}</div>
                      <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>
                        {rule.regulatory_framework}
                      </div>
                      <div style={{ fontSize: 11.5, color: "var(--text-secondary)", marginTop: 4 }}>
                        {rule.description}
                      </div>
                    </td>
                    <td>
                      <span style={{ 
                        fontSize: 11, 
                        fontWeight: 600, 
                        textTransform: "uppercase", 
                        color: "var(--text-muted)",
                        background: "var(--bg-surface-elevated)",
                        padding: "2px 6px",
                        borderRadius: 3
                      }}>
                        {rule.category}
                      </span>
                    </td>
                    <td>
                      <SeverityBadge severity={rule.severity} />
                    </td>
                    <td>
                      <div className="code-box" style={{ maxWidth: 260, fontSize: 11 }}>
                        {JSON.stringify(params, null, 1)}
                      </div>
                    </td>
                    <td>
                      <button
                        className="btn btn-outline btn-sm"
                        style={{
                          borderColor: rule.is_active ? "var(--status-resolved)" : "var(--border-subtle)",
                          color: rule.is_active ? "var(--status-resolved)" : "var(--text-muted)"
                        }}
                        onClick={() => handleToggle(rule)}
                        disabled={togglingId === rule.id || !isAdmin}
                      >
                        {rule.is_active ? (
                          <>
                            <ToggleRight size={16} />
                            <span>Active</span>
                          </>
                        ) : (
                          <>
                            <ToggleLeft size={16} />
                            <span>Disabled</span>
                          </>
                        )}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
