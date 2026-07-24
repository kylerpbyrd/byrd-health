import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/lib/query-client";
import { Layout } from "@/components/Layout";
import DashboardPage from "@/pages/DashboardPage";
import EntryPage from "@/pages/EntryPage";
import HistoryPage from "@/pages/HistoryPage";
import CycleDetailPage from "@/pages/CycleDetailPage";
import ProfilesPage from "@/pages/ProfilesPage";
import SettingsPage from "@/pages/SettingsPage";

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/entry" element={<EntryPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/history/:cycleId" element={<CycleDetailPage />} />
            <Route path="/profiles" element={<ProfilesPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
