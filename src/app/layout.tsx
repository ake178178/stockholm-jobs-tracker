import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Stockholm AI Jobs | Kobe Wang",
  description: "Daily AI × Telecom × Cloud job tracker for Stockholm — curated for Kobe Wang",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>
        <nav className="nav">
          <div className="nav-logo">
            🇸🇪 Stockholm <span>AI</span> Jobs
          </div>
          <span className="nav-chip">AI × Telecom × Cloud</span>
          <div className="nav-links">
            <a className="nav-link" href="/">今日职位</a>
            <a className="nav-link" href="/history/">历史记录</a>
          </div>
        </nav>
        {children}
        <footer>
          <p>
            数据来源：Amazon · Google · Microsoft · Ericsson · Nokia · Spotify · Klarna · Sinch ·
            每日 08:00 (Stockholm) 自动更新 ·{" "}
            <a href="https://github.com" target="_blank" rel="noreferrer">GitHub</a>
          </p>
        </footer>
      </body>
    </html>
  );
}
