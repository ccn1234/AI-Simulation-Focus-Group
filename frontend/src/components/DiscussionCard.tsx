import type { DiscussionResult, DiscussionMessage } from '../types/simulation';

type DiscussionCardProps = {
  discussion?: DiscussionResult;
};

const STANCE_LABELS: Record<string, string> = {
  agree: '찬성',
  disagree: '반대',
  neutral: '중립',
  changed_mind: '의견 변화',
  challenge: '반박',
  support: '동의',
};

const ISSUE_LABELS: Record<string, string> = {
  price: '가격',
  trust: '신뢰',
  privacy: '개인정보',
  convenience: '편의성',
  effectiveness: '효과 검증',
  habit: '습관 형성',
  brand: '브랜드',
};

function stanceLabel(stance: string): string {
  return STANCE_LABELS[stance] ?? stance;
}

function issueLabel(issue: string): string {
  return ISSUE_LABELS[issue] ?? issue;
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

function DiscussionMessageCard({ message }: { message: DiscussionMessage }) {
  return (
    <div className="discussion-message-card">
      <div className="discussion-message-header">
        <div>
          <span className="discussion-speaker-name">{message.speaker_name}</span>
          {message.speaker_role && (
            <span className="discussion-speaker-role">{message.speaker_role}</span>
          )}
        </div>
        <div className="discussion-badges">
          <span className={`stance-badge stance-badge--${message.stance}`}>{stanceLabel(message.stance)}</span>
          <span className="issue-badge">{issueLabel(message.related_issue)}</span>
        </div>
      </div>
      <p className="discussion-message-text">{message.message}</p>
    </div>
  );
}

function DiscussionCard({ discussion }: DiscussionCardProps) {
  const messages = discussion?.discussion_messages ?? [];
  const summary = discussion?.discussion_summary;
  const intentChanges = summary?.purchase_intent_changes ?? [];

  return (
    <div className="panel discussion-section">
      <h2>AI 소비자 토론</h2>

      {messages.length > 0 ? (
        <div className="discussion-timeline">
          {messages.map((message, index) => (
            <DiscussionMessageCard key={`${message.speaker_name}-${index}`} message={message} />
          ))}
        </div>
      ) : (
        <p className="meta empty-fallback">생성된 토론 내용이 없습니다.</p>
      )}

      <div className="discussion-summary-grid">
        <section className="discussion-summary-card">
          <h3>주요 충돌</h3>
          <ListOrFallback items={summary?.main_conflicts ?? []} fallback="발견된 의견 충돌이 없습니다." />
        </section>
        <section className="discussion-summary-card">
          <h3>합의된 의견</h3>
          <ListOrFallback items={summary?.agreements ?? []} fallback="합의된 의견이 없습니다." />
        </section>
        <section className="discussion-summary-card">
          <h3>바뀐 의견</h3>
          <ListOrFallback items={summary?.changed_opinions ?? []} fallback="의견 변화가 없습니다." />
        </section>
      </div>

      <section className="discussion-consensus">
        <h3>최종 그룹 결론</h3>
        <p>{summary?.final_group_consensus || '도출된 결론이 없습니다.'}</p>
      </section>

      <section className="discussion-intent-changes">
        <h3>구매의향 변화</h3>
        {intentChanges.length > 0 ? (
          <div className="intent-change-grid">
            {intentChanges.map((change) => (
              <div key={change.persona_name} className="intent-change-card">
                <div className="intent-change-name">{change.persona_name}</div>
                <div className="score-change">
                  <span className="score-change-before">{change.before_score}</span>
                  <span className="score-change-arrow">→</span>
                  <span
                    className={`score-change-after ${
                      change.after_score > change.before_score
                        ? 'score-change-after--up'
                        : change.after_score < change.before_score
                          ? 'score-change-after--down'
                          : ''
                    }`}
                  >
                    {change.after_score}
                  </span>
                </div>
                <p className="intent-change-reason">{change.change_reason}</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="meta empty-fallback">구매의향 변화가 기록되지 않았습니다.</p>
        )}
      </section>
    </div>
  );
}

export default DiscussionCard;
