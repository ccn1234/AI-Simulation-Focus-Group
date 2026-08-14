import type { PersonaResponse, SummaryReport } from '../types/simulation';

type Props = { report: SummaryReport; responses?: PersonaResponse[] };

export default function ExecutiveSummary({ report, responses = [] }: Props) {
  const priorities = report.improvement_priorities?.slice(0, 3) ?? [];
  const average = responses.length > 0
    ? (responses.reduce((sum, item) => sum + item.purchase_intent_score, 0) / responses.length).toFixed(1)
    : '-';
  const high = responses.filter((item) => item.purchase_intent_score >= 8).length;
  const mid = responses.filter((item) => item.purchase_intent_score >= 5 && item.purchase_intent_score < 8).length;
  const low = responses.filter((item) => item.purchase_intent_score < 5).length;
  return <section className="panel executive-summary">
    <div className="executive-summary-heading"><div><p className="eyebrow">Decision brief</p><h2>Executive Summary</h2></div><div className="executive-score"><strong>{report.overall_score}</strong><span>/10</span><small>종합 구매 가능성</small></div></div>
      <div className="executive-score-track"><span style={{ width: `${Math.max(0, Math.min(Number(report.overall_score ?? 0), 10)) * 10}%` }} /></div>
      <div className="intent-distribution"><span>구매 의향 분포</span><div className="distribution-bar"><i className="distribution-high" style={{ width: `${responses.length ? high / responses.length * 100 : 0}%` }} /><i className="distribution-mid" style={{ width: `${responses.length ? mid / responses.length * 100 : 0}%` }} /><i className="distribution-low" style={{ width: `${responses.length ? low / responses.length * 100 : 0}%` }} /></div><small>높음 {high}명 · 보통 {mid}명 · 낮음 {low}명</small></div>
      <div className="executive-grid">
        <article className="executive-insight executive-insight--score"><span>페르소나 평균 구매 의향</span><p>{average}<small>/10</small></p></article>
      <article className="executive-insight executive-insight--positive"><span>가장 강한 긍정 요소</span><p>{report.key_positive_reactions?.[0] || '긍정 반응이 없습니다.'}</p></article>
      <article className="executive-insight executive-insight--warning"><span>가장 큰 구매 장벽</span><p>{report.weakest_point || report.key_negative_reactions?.[0] || '구매 장벽이 없습니다.'}</p></article>
      <article className="executive-insight"><span>가장 적합한 타깃</span><p>{report.strongest_target_segment || '타깃 분석 결과가 없습니다.'}</p></article>
    </div>
    <div className="executive-actions"><div><h3>우선 실행할 개선 과제</h3>{priorities.length ? <ol>{priorities.map((item) => <li key={item}>{item}</li>)}</ol> : <p className="meta">개선 과제가 없습니다.</p>}</div><div><h3>다음 액션</h3><p>{report.recommended_next_actions?.[0] || '추천 액션이 없습니다.'}</p></div></div>
  </section>;
}
