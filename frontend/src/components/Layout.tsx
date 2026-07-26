import { NavLink } from "react-router-dom";
import { cn } from "@/lib/utils";
import { Activity } from "lucide-react";

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/calendar", label: "Calendar" },
  { to: "/entry", label: "Log Entry" },
  { to: "/history", label: "History" },
  { to: "/profiles", label: "Profiles" },
  { to: "/settings", label: "Settings" },
];

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:rounded focus:bg-white focus:px-4 focus:py-2 focus:text-sm focus:shadow"
      >
        Skip to content
      </a>
      <header className="sticky top-0 z-50 border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
          <NavLink to="/" className="flex items-center gap-2" aria-label="Byrd Health home">
            <Activity className="h-6 w-6 text-primary" aria-hidden="true" />
            <span
              className="text-lg font-bold"
              style={{ color: "#9c27b0" }}
            >
              Byrd Health
            </span>
          </NavLink>
          <nav className="flex gap-1 overflow-x-auto">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                aria-label={item.label}
                className={({ isActive }) =>
                  cn(
                    "rounded-md px-3 py-2 text-sm font-medium transition-colors whitespace-nowrap",
                    isActive
                      ? "bg-accent text-accent-foreground"
                      : "text-muted-foreground hover:text-foreground hover:bg-accent/50"
                  )
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main id="main-content" className="mx-auto max-w-4xl px-4 py-6">{children}</main>
    </div>
  );
}
