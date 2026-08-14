import type { SummaryReport } from '../types/simulation';

type SummaryReportCardProps = {
  report: SummaryReport;
};

function scoreLevel(score: number): 'low' | 'mid' | 'high' {
  if (score >= 8) return 'high';
  if (score >= 5) return 'mid';
  return 'low';
}

function ListOrFallback({ items, fallback }: { items: string[]; fallback: string }) {
  if (!items || items.length === 0) {
    return <p className="meta empty-fallback">{fallback}</p>;
  }
  return (
    <ul className="spaced-list">
      {items.map((item) => <li key={item}>{item}</li>)}
    </ul>
  );
}

function SummaryReportCard({ report }: SummaryReportCardProps) {
  const score = report.overall_score ?? 0;
  const level = scoreLevel(score);

  return (
    <div className="panel summary">
      <h2>Moderator 요약 리포트</h2>

      <div className={`score-card score-card--${level}`}>
        <div className="score-card-value">
          <span className="score-card-number">{score}</span>
          <span className="score-card-max">/10</span>
        </div>
        <div className="score-card-label">종합 점수</div>
      </div>

      <section className="key-insights">
        <h3>핵심 인사이트</h3>
        <ListOrFallback items={report.key_insights} fallback="도출된 핵심 인사이트가 없습니다." />
      </section>

      <div className="reaction-grid">
        <section className="reaction-box reaction-box--positive">
          <h3>긍정 반응</h3>
          <ListOrFallback items={report.key_positive_reactions} fallback="수집된 긍정 반응이 없습니다." />
        </section>
        <section className="reaction-box reaction-box--negative">
          <h3>부정 반응</h3>
          <ListOrFallback items={report.key_negative_reactions} fallback="수집된 부정 반응이 없습니다." />
        </section>
      </div>

      <div className="insight-grid">
        <section className="insight-card">
          <span className="insight-card-tag">가장 강한 타깃</span>
          <p>{report.strongest_target_segment || '분석된 내용이 없습니다.'}</p>
        </section>
        <section className="insight-card">
          <span className="insight-card-tag insight-card-tag--warn">가장 약한 부분</span>
          <p>{report.weakest_point || '분석된 내용이 없습니다.'}</p>
        </section>
      </div>

      <section className="improvement-priorities">
        <h3>개선 우선순위</h3>
        <ListOrFallback items={report.improvement_priorities} fallback="제안된 개선 우선순위가 없습니다." />
      </section>

      <section className="action-plan">
        <h3>다음 액션</h3>
        <ListOrFallback items={report.recommended_next_actions} fallback="제안된 다음 액션이 없습니다." />
      </section>
    </div>
  );
}

export default SummaryReportCard;
