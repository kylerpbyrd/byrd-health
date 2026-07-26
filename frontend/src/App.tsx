import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner";
import { queryClient } from "@/lib/query-client";
import { Layout } from "@/components/Layout";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import DashboardPage from "@/pages/DashboardPage";
import EntryPage from "@/pages/EntryPage";
import HistoryPage from "@/pages/HistoryPage";
import CycleDetailPage from "@/pages/CycleDetailPage";
import ProfilesPage from "@/pages/ProfilesPage";
import SettingsPage from "@/pages/SettingsPage";

declare global {
  interface Window {
    __INGRESS_PATH__?: string;
  }
}

const BASENAME = (window as any).__INGRESS_PATH__ || "/";

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Toaster position="bottom-right" richColors />
      <BrowserRouter basename={BASENAME}>
        <Layout>
          <ErrorBoundary>
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/entry" element={<EntryPage />} />
              <Route path="/history" element={<HistoryPage />} />
              <Route path="/history/:cycleId" element={<CycleDetailPage />} />
              <Route path="/profiles" element={<ProfilesPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </ErrorBoundary>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
