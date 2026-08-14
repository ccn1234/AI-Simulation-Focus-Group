import type { Persona, PersonaResponse } from '../types/simulation';

type PersonaCardProps = {
  persona?: Persona;
  response: PersonaResponse;
};

const REACTION_TYPE_LABELS: Record<string, string> = {
  skeptical: '회의적',
  impulsive: '즉흥적',
  rational: '이성적',
  price_sensitive: '가격민감',
  brand_loyal: '브랜드충성',
  convenience_first: '편의우선',
  quality_first: '품질우선',
  novelty_seeker: '신기술추구',
  risk_averse: '위험회피',
  pragmatic: '실용적',
};

function intentLevel(score: number): 'low' | 'mid' | 'high' {
  if (score >= 8) return 'high';
  if (score >= 5) return 'mid';
  return 'low';
}

function intentLabel(level: 'low' | 'mid' | 'high'): string {
  if (level === 'high') return '높음';
  if (level === 'mid') return '중간';
  return '낮음';
}

function reactionTypeLabel(reactionType?: string): string {
  if (!reactionType) return '';
  return REACTION_TYPE_LABELS[reactionType] ?? reactionType;
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

function TagList({ items }: { items: string[] }) {
  if (!items || items.length === 0) {
    return <span className="meta">-</span>;
  }
  return (
    <span className="tag-list">
      {items.map((item) => <span key={item} className="tag-chip">{item}</span>)}
    </span>
  );
}

function PersonaCard({ persona, response }: PersonaCardProps) {
  const score = response.purchase_intent_score ?? 0;
  const level = intentLevel(score);

  return (
    <article className="panel persona-card">
      <div className="persona-card-header">
        <div className="persona-card-title-row">
          <h3>
            {persona ? `${persona.name} · ${persona.age}세 · ${persona.job}` : '페르소나 정보 없음'}
          </h3>
          {persona?.reaction_type && (
            <span className="reaction-type-badge">{reactionTypeLabel(persona.reaction_type)}</span>
          )}
        </div>
        {persona && (
          <p className="meta">{persona.gender} / {persona.income_level} / {persona.personality}</p>
        )}
        {persona?.lifestyle && (
          <p className="persona-lifestyle">{persona.lifestyle}</p>
        )}
      </div>

      {persona && (
        <div className="quick-facts">
          <div className="quick-fact">
            <span className="quick-fact-label">AI 친숙도</span>
            <span className="quick-fact-value">{persona.ai_familiarity || '-'}</span>
          </div>
          <div className="quick-fact">
            <span className="quick-fact-label">가격 민감도</span>
            <span className="quick-fact-value">{persona.price_sensitivity || '-'}</span>
          </div>
          <div className="quick-fact">
            <span className="quick-fact-label">의사결정</span>
            <span className="quick-fact-value">{persona.decision_style || '-'}</span>
          </div>
        </div>
      )}

      {persona && persona.current_solutions.length > 0 && (
        <p className="persona-current-solutions">
          <strong>현재 대안:</strong> <TagList items={persona.current_solutions} />
        </p>
      )}

      <div className={`intent-meter intent-meter--${level}`}>
        <div className="intent-meter-top">
          <span className="intent-meter-badge">구매의향 {intentLabel(level)}</span>
          <span className="intent-meter-score">{score}/10</span>
        </div>
        <div className="intent-meter-track">
          <div className="intent-meter-fill" style={{ width: `${Math.max(0, Math.min(score, 10)) * 10}%` }} />
        </div>
      </div>

      {response.first_impression && (
        <p className="persona-first-impression">{response.first_impression}</p>
      )}

      {(response.memorable_quote || response.first_impression) && (
        <blockquote className="persona-quote">
          “{response.memorable_quote || response.first_impression}”
        </blockquote>
      )}

      {persona?.pain_point && (
        <p className="persona-pain-point"><strong>고민:</strong> {persona.pain_point}</p>
      )}

      <section className="persona-section">
        <h4>좋았던 점</h4>
        <ListOrFallback items={response.positive_points} fallback="언급된 긍정 포인트가 없습니다." />
      </section>

      <section className="persona-section persona-section--concern">
        <h4>구매장벽 · 우려점</h4>
        {persona?.purchase_barrier && (
          <p className="persona-barrier"><strong>구매장벽:</strong> {persona.purchase_barrier}</p>
        )}
        <ListOrFallback items={response.concerns} fallback="언급된 우려점이 없습니다." />
      </section>

      <section className="persona-improvement">
        <h4>개선 제안</h4>
        <p>{response.suggested_improvement || '제안된 개선 사항이 없습니다.'}</p>
      </section>

      {persona && (
        <details className="persona-more">
          <summary>추가 정보 보기</summary>
          <div className="persona-more-body">
            <p>
              <strong>거주지역:</strong> {persona.region || '-'} ·{' '}
              <strong>결혼상태:</strong> {persona.marital_status || '-'} ·{' '}
              <strong>자녀:</strong> {persona.has_children ? '있음' : '없음'}
            </p>
            <p><strong>브랜드 민감도:</strong> {persona.brand_sensitivity || '-'}</p>
            <p><strong>자주 쓰는 앱:</strong> <TagList items={persona.frequently_used_apps} /></p>
            <p><strong>정보 채널:</strong> <TagList items={persona.information_channels} /></p>
            {persona.past_failure_experience && (
              <p><strong>과거 실패 경험:</strong> {persona.past_failure_experience}</p>
            )}
          </div>
        </details>
      )}
    </article>
  );
}

export default PersonaCard;
