import { getAllDates, getDataForDate } from "@/lib/jobs";
import Link from "next/link";

export const dynamic = "force-static";

export default function HistoryPage() {
  const dates = getAllDates();

  return (
    <>
      <div className="hero">
        <div className="hero-inner">
          <div>
            <div className="hero-title">📅 历史职位记录</div>
            <div className="hero-sub">查看每日爬取的斯德哥尔摩 AI 职位归档</div>
          </div>
          <div className="hero-stats">
            <div className="hstat">
              <div className="hstat-n orange">{dates.length}</div>
              <div className="hstat-l">天记录</div>
            </div>
          </div>
        </div>
      </div>

      <div className="container">
        <div className="sec-title">所有日期</div>

        {dates.length === 0 ? (
          <div className="empty-state">
            <h3>暂无历史记录</h3>
            <p>请先运行 <code>python scripts/fetch_jobs.py</code> 生成数据</p>
          </div>
        ) : (
          <div className="history-grid">
            {dates.map((date) => {
              const data = getDataForDate(date);
              if (!data) return null;
              return (
                <div key={date} className="history-card">
                  <div className="hcard-date">{date}</div>
                  <div className="hcard-stats">
                    <div className="hstat-sm">
                      <div className="n">{data.stats.total}</div>
                      <div className="l">职位总数</div>
                    </div>
                    <div className="hstat-sm">
                      <div className="n">{data.stats.new_count}</div>
                      <div className="l">新增职位</div>
                    </div>
                  </div>
                  {data.stats.new_count > 0 && (
                    <div className="hcard-new">🆕 {data.stats.new_count} 个新职位</div>
                  )}
                  <Link href={`/history/${date}/`} className="hcard-btn">
                    查看详情 →
                  </Link>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </>
  );
}
