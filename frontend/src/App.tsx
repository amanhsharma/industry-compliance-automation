import { useState, useEffect } from "react";
import "./styles/theme.css";
import "./styles/components.css";
import { Sidebar } from "./components/layout/Sidebar";
import { TopBar } from "./components/layout/TopBar";
import { DashboardPage } from "./pages/DashboardPage";
import { UploadPage } from "./pages/UploadPage";
import { ViolationsPage } from "./pages/ViolationsPage";
import { ReportsPage } from "./pages/ReportsPage";
import { RulesPage } from "./pages/RulesPage";
import { LoginPage } from "./pages/LoginPage";
import { 
  api, 
  type User, 
  type DashboardSummary, 
  type Violation, 
  type Dataset, 
  type ComplianceRule 
} from "./services/api";

export function App() {
  const [user, setUser] = useState<User | null>(null);
  const [currentTab, setCurrentTab] = useState<string>("dashboard");
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [violations, setViolations] = useState<Violation[]>([]);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [rules, setRules] = useState<ComplianceRule[]>([]);
  const [selectedViolation, setSelectedViolation] = useState<Violation | null>(null);
  const [loadingInitial, setLoadingInitial] = useState(true);

  // Check auth session on startup
  useEffect(() => {
    const token = localStorage.getItem("apex_access_token");
    if (token) {
      api.getMe()
        .then((userData) => {
          setUser(userData);
          refreshTelemetry();
        })
        .catch(() => {
          localStorage.removeItem("apex_access_token");
          setUser(null);
        })
        .finally(() => setLoadingInitial(false));
    } else {
      setLoadingInitial(false);
    }
  }, []);

  const refreshTelemetry = async () => {
    try {
      const [sum, vios, dsets, rls] = await Promise.all([
        api.getDashboardSummary(),
        api.listViolations(),
        api.listDatasets(),
        api.listRules(),
      ]);
      setSummary(sum);
      setViolations(vios);
      setDatasets(dsets);
      setRules(rls);
    } catch (err) {
      console.error("Failed to load telemetry", err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("apex_access_token");
    setUser(null);
    setSummary(null);
    setViolations([]);
    setDatasets([]);
  };

  if (loadingInitial) {
    return (
      <div style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "var(--bg-app)",
        color: "var(--text-muted)",
        fontSize: 13
      }}>
        Initializing Apex Compliance Console...
      </div>
    );
  }

  if (!user) {
    return <LoginPage onLoginSuccess={(u) => { setUser(u); refreshTelemetry(); }} />;
  }

  const openViolationsCount = summary?.open_violations ?? 0;

  return (
    <div className="app-layout">
      <Sidebar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        user={user}
        openViolationsCount={openViolationsCount}
        onLogout={handleLogout}
      />

      <div className="main-wrapper">
        <TopBar
          currentTab={currentTab}
          onQuickUpload={() => setCurrentTab("upload")}
          onQuickReport={() => setCurrentTab("reports")}
        />

        <main className="content-body">
          {currentTab === "dashboard" && (
            <DashboardPage
              summary={summary}
              recentViolations={violations}
              onSelectViolation={(v) => {
                setSelectedViolation(v);
                setCurrentTab("violations");
              }}
              onNavigate={setCurrentTab}
            />
          )}

          {currentTab === "upload" && (
            <UploadPage
              datasets={datasets}
              onUploadSuccess={refreshTelemetry}
            />
          )}

          {currentTab === "violations" && (
            <ViolationsPage
              violations={violations}
              selectedViolation={selectedViolation}
              onSelectViolation={setSelectedViolation}
              onViolationUpdated={refreshTelemetry}
            />
          )}

          {currentTab === "reports" && (
            <ReportsPage
              summary={summary}
              tenantName={user.tenant?.name || "Meridian Financial Services"}
            />
          )}

          {currentTab === "rules" && (
            <RulesPage
              rules={rules}
              isAdmin={user.role === "admin"}
              onRuleToggled={refreshTelemetry}
            />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
