import { Suspense, lazy } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner";
import { queryClient } from "@/lib/query-client";
import { Layout } from "@/components/Layout";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { Skeleton } from "@/components/Skeleton";

const DashboardPage = lazy(() => import("@/pages/DashboardPage"));
const EntryPage = lazy(() => import("@/pages/EntryPage"));
const HistoryPage = lazy(() => import("@/pages/HistoryPage"));
const CycleDetailPage = lazy(() => import("@/pages/CycleDetailPage"));
const ProfilesPage = lazy(() => import("@/pages/ProfilesPage"));
const SettingsPage = lazy(() => import("@/pages/SettingsPage"));

declare global {
  interface Window {
    __INGRESS_PATH__?: string;
  }
}

const BASENAME = (window as any).__INGRESS_PATH__ || "/";

function PageFallback() {
  return (
    <div className="space-y-4 py-4">
      <Skeleton className="h-8 w-48" />
      <Skeleton className="h-[220px] w-full rounded-lg" />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Skeleton className="h-24 rounded-lg" />
        <Skeleton className="h-24 rounded-lg" />
        <Skeleton className="h-24 rounded-lg" />
      </div>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Toaster position="bottom-right" richColors />
      <BrowserRouter basename={BASENAME}>
        <Layout>
          <ErrorBoundary>
            <Suspense fallback={<PageFallback />}>
              <Routes>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/entry" element={<EntryPage />} />
                <Route path="/history" element={<HistoryPage />} />
                <Route path="/history/:cycleId" element={<CycleDetailPage />} />
                <Route path="/profiles" element={<ProfilesPage />} />
                <Route path="/settings" element={<SettingsPage />} />
              </Routes>
            </Suspense>
          </ErrorBoundary>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
