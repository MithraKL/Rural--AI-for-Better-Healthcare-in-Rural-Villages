import { NavLink, Outlet } from "react-router-dom";
import clsx from "clsx";

const NAV = [
  { to: "/", label: "Overview", icon: "◧" },
  { to: "/villages", label: "Village Intelligence", icon: "◎" },
  { to: "/risk", label: "Risk & Prediction", icon: "△" },
  { to: "/hidden-gaps", label: "Hidden Gaps", icon: "◐" },
  { to: "/interventions", label: "Intervention Planner", icon: "✚" },
  { to: "/simulator", label: "What-If Simulator", icon: "⇄" },
  { to: "/resources", label: "Resource Optimizer", icon: "▤" },
  { to: "/facilities", label: "Facilities", icon: "▣" },
  { to: "/data", label: "Data Explorer", icon: "▦" },
  { to: "/methodology", label: "Methodology", icon: "ℹ" },
];

export default function Layout() {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-ink-50">
      <aside className="flex w-64 shrink-0 flex-col border-r border-ink-200 bg-ink-950 text-ink-100">
        <div className="flex items-center gap-2 border-b border-white/10 px-5 py-5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-500 text-sm font-bold text-white">RC</div>
          <div>
            <p className="text-sm font-bold leading-tight text-white">RuralCare AI</p>
            <p className="text-[11px] text-ink-400">Decision Intelligence</p>
          </div>
        </div>
        <nav className="flex-1 overflow-y-auto px-2 py-3">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                clsx(
                  "mb-1 flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive ? "bg-brand-600 text-white" : "text-ink-300 hover:bg-white/5 hover:text-white"
                )
              }
            >
              <span className="w-4 text-center text-[13px] opacity-80">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-white/10 px-4 py-3 text-[11px] text-ink-500">
          District Health Officer Console
          <br />
          v1.0.0 — Hackathon Build
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-ink-200 bg-white px-6 py-3">
          <div>
            <p className="text-sm font-semibold text-ink-900">Rural Healthcare Decision Console</p>
            <p className="text-xs text-ink-500">Where is the problem → why → what next → what should we do → where should resources go</p>
          </div>
          <span
            className="rounded-full bg-amber-100 px-3 py-1 text-[11px] font-semibold text-amber-800 ring-1 ring-amber-200"
            title="District/village geography and NFHS-5/AHS district indicators are real published data. Facility-level utilization and Anganwadi figures are synthetic (HMIS/ICDS have no public bulk-download source). See Data Explorer for the source-by-source breakdown."
          >
            MIXED DATA — real geography &amp; district surveys, synthetic utilization (see Data Explorer)
          </span>
        </header>
        <main className="min-w-0 flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
