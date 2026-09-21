import React from "react";

export const SeverityBadge: React.FC<{ severity: string }> = ({ severity }) => {
  const sev = severity.toUpperCase();
  const badgeClass = `badge badge-${sev.toLowerCase()}`;
  return <span className={badgeClass}>{sev}</span>;
};

export const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const stat = status.toUpperCase();
  const display = stat.replace("_", " ");
  const badgeClass = `badge badge-${stat.toLowerCase()}`;
  return <span className={badgeClass}>{display}</span>;
};
