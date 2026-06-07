import { getAllDates, getDataForDate, COMPANY_META, scoreLabel } from "@/lib/jobs";
import type { Job } from "@/lib/types";
import Link from "next/link";
import { notFound } from "next/navigation";

export const dynamic = "force-static";

export async function generateStaticParams() {
  return getAllDates().map((date) => ({ date }));
}

function JobCard({ job }: { job: Job }) {
  const meta = COMPANY_META[job.company_key] || { color: "#6B7280", logo: "🏢" };
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
        <span className="posted-date">{job.posted ? `发布: ${job.posted}` : ""}</span>
        <a href={job.url} target="_blank" rel="noreferrer" className="apply-btn">查看申请 →</a>
      </div>
    </div>
  );
}

export default async function DatePage({ params }: { params: Promise<{ date: string }> }) {
  const { date } = await params;
  const data = getDataForDate(date);
  if (!data) notFound();

  const { jobs, stats, generated_at } = data;
  const generatedTime = new Date(generated_at).toLocaleString("zh-CN", {
    timeZone: "Europe/Stockholm",
    year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit",
  });

  return (
    <>
      <div className="hero">
        <div className="hero-inner">
          <div>
            <div className="hero-title">📋 职位记录 · {date}</div>
            <div className="hero-sub">更新于 {generatedTime}</div>
          </div>
          <div className="hero-stats">
            <div className="hstat">
              <div className="hstat-n orange">{stats.total}</div>
              <div className="hstat-l">职位总数</div>
            </div>
            <div className="hstat">
              <div className="hstat-n green">{stats.new_count}</div>
              <div className="hstat-l">当日新增</div>
            </div>
          </div>
        </div>
      </div>

      <div className="container">
        <div className="date-nav">
          <Link href="/history/" className="back-link">← 返回历史列表</Link>
          <span className="date-nav-label">查看日期：</span>
          <span className="date-nav-date">{date}</span>
        </div>

        {jobs.filter((j) => j.match_score >= 70).length > 0 && (
          <>
            <div className="sec-title">⭐ S 级强匹配</div>
            <div className="jobs-grid">
              {jobs.filter((j) => j.match_score >= 70).map((j) => <JobCard key={j.id} job={j} />)}
            </div>
          </>
        )}

        {jobs.filter((j) => j.match_score >= 50 && j.match_score < 70).length > 0 && (
          <>
            <div className="sec-title">A 级推荐</div>
            <div className="jobs-grid">
              {jobs.filter((j) => j.match_score >= 50 && j.match_score < 70).map((j) => <JobCard key={j.id} job={j} />)}
            </div>
          </>
        )}

        {jobs.filter((j) => j.match_score < 50).length > 0 && (
          <>
            <div className="sec-title">B 级参考</div>
            <div className="jobs-grid">
              {jobs.filter((j) => j.match_score < 50).map((j) => <JobCard key={j.id} job={j} />)}
            </div>
          </>
        )}

        {jobs.length === 0 && (
          <div className="empty-state">
            <h3>该日无匹配职位</h3>
          </div>
        )}
      </div>
    </>
  );
}
