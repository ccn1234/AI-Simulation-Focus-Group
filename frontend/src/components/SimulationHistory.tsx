import { useEffect, useState } from 'react';
import { token } from './AuthGate';
import ProductAnalysisCard from './ProductAnalysisCard';
import SummaryReportCard from './SummaryReportCard';
import DiscussionCard from './DiscussionCard';
import PersonaCard from './PersonaCard';

type Item = { id: number; product_name: string; target_audience: string; status: string; created_at: string; completed_at?: string | null };
const API = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export default function SimulationHistory() {
  const [items, setItems] = useState<Item[]>([]);
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [selected, setSelected] = useState<number | null>(null);
  const [detail, setDetail] = useState<any>(null);
  const [compareIds, setCompareIds] = useState<number[]>([]);
  const [insights, setInsights] = useState<any[]>([]);
  const [comparison, setComparison] = useState<any[]>([]);
  const [error, setError] = useState('');

  const load = async () => {
    setError('');
    const query = new URLSearchParams({ limit: '50' });
    if (search) query.set('search', search);
    if (status) query.set('status', status);
    const response = await fetch(`${API}/simulations?${query}`, { headers: { Authorization: `Bearer ${token() ?? ''}` } });
    if (!response.ok) throw new Error('시뮬레이션 이력을 불러오지 못했습니다.');
    setItems(await response.json());
  };
  useEffect(() => { load().catch((e) => setError(e.message)); }, [status]);
  const headers = { Authorization: `Bearer ${token() ?? ''}` };
  const open = async (id: number) => { setSelected(id); const [response, insightResponse] = await Promise.all([fetch(`${API}/simulations/${id}`, { headers }), fetch(`${API}/simulations/${id}/insights`, { headers })]); setDetail(await response.json()); if (insightResponse.ok) setInsights(await insightResponse.json()); };
  const remove = async (id: number) => { if (!confirm('이 시뮬레이션을 삭제할까요?')) return; await fetch(`${API}/simulations/${id}`, { method: 'DELETE', headers }); setSelected(null); setDetail(null); load(); };
  const compare = async () => { if (compareIds.length < 2) return; const response = await fetch(`${API}/simulations/compare?${compareIds.map((id) => `ids=${id}`).join('&')}`, { headers }); if (response.ok) setComparison(await response.json()); };

  return <section className="panel history-panel">
    <div className="history-toolbar"><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="상품명 검색" /><select value={status} onChange={(e) => setStatus(e.target.value)}><option value="">전체 상태</option><option value="succeeded">성공</option><option value="pending">진행 중</option><option value="failed">실패</option></select><button onClick={() => load().catch((e) => setError(e.message))}>검색</button></div>
    {error && <p className="error-message">{error}</p>}
    {!items.length && !error && <p className="meta">저장된 시뮬레이션이 없습니다.</p>}
    <button disabled={compareIds.length < 2} onClick={compare}>선택 결과 비교 ({compareIds.length})</button>
    <div className="history-list">{items.map((item) => <article className="history-item" key={item.id}><input type="checkbox" checked={compareIds.includes(item.id)} onChange={() => setCompareIds((ids) => ids.includes(item.id) ? ids.filter((id) => id !== item.id) : ids.length < 3 ? [...ids, item.id] : ids)} /><div><strong>{item.product_name}</strong><p>{item.target_audience} · {new Date(item.created_at).toLocaleString()}</p></div><span className={`status status--${item.status}`}>{item.status}</span><button onClick={() => open(item.id)}>상세</button><button onClick={() => remove(item.id)}>삭제</button></article>)}</div>
    {selected && detail && <div className="history-detail" id="insights"><h2>시뮬레이션 #{selected}</h2><p>상태: <strong>{detail.status}</strong></p><section className="insight-section"><div className="insight-heading"><div><h3>키워드 인사이트</h3><p>상품·광고 문구와 Persona 반응에서 자주 등장하며 구매의도에 영향을 준 핵심 키워드입니다.</p></div><span className="insight-count">상위 {Math.min(5, insights.length)}개</span></div>{insights.length ? <div className="keyword-insights">{insights.slice(0,5).map((item)=><div className="keyword-insight" key={item.keyword}><strong>{item.keyword}</strong><small>{item.category} · {item.matched_personas}명 Persona · 평균 구매의도 {item.average_purchase_intent ?? '-'}</small><div className="insight-bar"><span className="positive" style={{width:`${Math.min(100,item.positive_mentions*20)}%`}} /><span className="negative" style={{width:`${Math.min(100,item.negative_mentions*20)}%`}} /></div><small>긍정 {item.positive_mentions} · 부정 {item.negative_mentions} · 중립 {item.neutral_mentions} · 감성 지수 {item.sentiment_ratio}</small></div>)}</div> : <p className="meta">연결된 키워드 인사이트가 없습니다.</p>}{insights.length > 5 && <details className="more-insights"><summary>나머지 키워드 {insights.length - 5}개 보기</summary><div className="keyword-insights">{insights.slice(5).map((item)=><div className="keyword-insight" key={item.keyword}><strong>{item.keyword}</strong><small>{item.category} · {item.matched_personas}명 Persona · 평균 구매의도 {item.average_purchase_intent ?? '-'}</small></div>)}</div></details>}</section><ProductAnalysisCard analysis={detail.product_analysis} /><SummaryReportCard report={detail.summary_report} /><DiscussionCard discussion={detail.discussion_result} /><section className="panel"><h2>Persona별 반응</h2><div className="card-grid">{(detail.responses ?? []).map((response:any) => <PersonaCard key={response.persona_id} persona={(detail.personas ?? []).find((persona:any)=>persona.id===response.persona_id)} response={response} />)}</div></section></div>}
    {!!comparison.length && <div className="history-detail"><h2>비교 결과</h2>{comparison.map((item) => <div key={item.id}><h3>#{item.id} {item.product_name}</h3><p>종합 점수: {item.summary_report?.overall_score ?? '-'}</p><p>핵심 인사이트: {item.summary_report?.key_insights?.join(', ') ?? '-'}</p></div>)}</div>}
  </section>;
}
