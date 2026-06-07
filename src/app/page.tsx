import { getLatestData, COMPANY_META, scoreLabel } from "@/lib/jobs";
import type { Job } from "@/lib/types";

export const dynamic = "force-static";
export const revalidate = false;

function JobCard({ job }: { job: Job }) {
  const meta = COMPANY_META[job.company_key] || {
    color: "#6B7280",
    logo: "🏢",
  };
  const { label: scoreL } = scoreLabel(job.match_score);

  return (
    <div className={`job-card${job.is_new ? " is-new" : ""}`}>
      <div className="card-accent" style={{ background: meta.color }} />
      <div className="card-body">
        <div className="card-top">
          <div className="co-logo">{meta.logo}</div>
          <div className="card-title-block">
            <div className="job-title" title={job.title}>{job.title}</div>
            <div className="job-company">{job.company}</div>
          </div>
          <div className={`score-badge score-${scoreL}`}>{scoreL}</div>
        </div>

        <div className="card-meta">
          <span className="pill pill-loc">📍 {job.location}</span>
          {job.job_type && <span className="pill pill-type">{job.job_type}</span>}
          {job.team && <span className="pill pill-loc">{job.team}</span>}
        </div>

        {job.match_reasons.length > 0 && (
          <div className="match-reasons">
            {job.match_reasons.slice(0, 5).map((r) => (
              <span key={r} className="reason-tag">{r}</span>
            ))}
          </div>
        )}
      </div>

      <div className="card-footer-bar">
        <span className="posted-date">
          {job.posted ? `发布: ${job.posted}` : ""}
        </span>
        <a
          href={job.url}
          target="_blank"
          rel="noreferrer"
          className="apply-btn"
        >
          查看申请 →
        </a>
      </div>
    </div>
  );
}

export default function HomePage() {
  const data = getLatestData();

  if (!data) {
    return (
      <>
        <div className="hero">
          <div className="hero-inner">
            <div>
              <div className="hero-title">每日 AI 职位追踪</div>
              <div className="hero-sub">斯德哥尔摩 · AI × Telecom × Cloud</div>
            </div>
          </div>
        </div>
        <div className="container">
          <div className="empty-state">
            <h3>暂无数据</h3>
            <p>首次运行请执行 GitHub Actions 或手动运行 <code>python scripts/fetch_jobs.py</code></p>
          </div>
        </div>
      </>
    );
  }

  const { jobs, stats, date, generated_at } = data;
  const generatedTime = new Date(generated_at).toLocaleString("zh-CN", {
    timeZone: "Europe/Stockholm",
    year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit",
  });

  // Group by company for summary
  const companies = Object.keys(COMPANY_META);

  return (
    <>
      <div className="hero">
        <div className="hero-inner">
          <div>
            <div className="hero-title">📋 每日 AI 职位追踪 · {date}</div>
            <div className="hero-sub">
              斯德哥尔摩 大公司 AI × Telecom × Cloud · 更新于 {generatedTime}
            </div>
          </div>
          <div className="hero-stats">
            <div className="hstat">
              <div className="hstat-n orange">{stats.total}</div>
              <div className="hstat-l">匹配职位</div>
            </div>
            <div className="hstat">
              <div className="hstat-n green">{stats.new_count}</div>
              <div className="hstat-l">今日新增</div>
            </div>
            <div className="hstat">
              <div className="hstat-n">{Object.keys(stats.by_company).length}</div>
              <div className="hstat-l">家公司</div>
            </div>
          </div>
        </div>
      </div>

      <div className="container">
        {/* Summary chips */}
        <div className="summary-bar">
          {companies
            .filter((k) => stats.by_company[COMPANY_META[k].label])
            .map((k) => (
              <div key={k} className="summary-chip">
                <span className="n">{stats.by_company[COMPANY_META[k].label] ?? 0}</span>
                <span className="l">{COMPANY_META[k].logo} {COMPANY_META[k].label}</span>
              </div>
            ))}
        </div>

        {/* S-tier */}
        {jobs.filter((j) => j.match_score >= 70).length > 0 && (
          <>
            <div className="sec-title">⭐ S 级强匹配（分数 ≥ 70）</div>
            <div className="jobs-grid">
              {jobs
                .filter((j) => j.match_score >= 70)
                .map((j) => <JobCard key={j.id} job={j} />)}
            </div>
          </>
        )}

        {/* A-tier */}
        {jobs.filter((j) => j.match_score >= 50 && j.match_score < 70).length > 0 && (
          <>
            <div className="sec-title">A 级推荐（分数 50–69）</div>
            <div className="jobs-grid">
              {jobs
                .filter((j) => j.match_score >= 50 && j.match_score < 70)
                .map((j) => <JobCard key={j.id} job={j} />)}
            </div>
          </>
        )}

        {/* B/C-tier */}
        {jobs.filter((j) => j.match_score < 50).length > 0 && (
          <>
            <div className="sec-title">B 级参考（分数 &lt; 50）</div>
            <div className="jobs-grid">
              {jobs
                .filter((j) => j.match_score < 50)
                .map((j) => <JobCard key={j.id} job={j} />)}
            </div>
          </>
        )}

        {jobs.length === 0 && (
          <div className="empty-state">
            <h3>今日暂无匹配职位</h3>
            <p>爬虫已运行，各公司暂无新开放的匹配职位。明日再查看。</p>
          </div>
        )}
      </div>
    </>
  );
}
