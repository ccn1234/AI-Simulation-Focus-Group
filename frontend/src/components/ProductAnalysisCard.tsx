import type { ProductAnalysis } from '../types/simulation';

type ProductAnalysisCardProps = {
  analysis: ProductAnalysis;
};

function AnalysisList({ title, items }: { title: string; items: string[] }) {
  return (
    <section className="analysis-item">
      <h4>{title}</h4>
      {items.length > 0 ? (
        <ul>{items.map((item) => <li key={item}>{item}</li>)}</ul>
      ) : (
        <p className="meta">분석된 내용이 없습니다.</p>
      )}
    </section>
  );
}

function ProductAnalysisCard({ analysis }: ProductAnalysisCardProps) {
  return (
    <div className="panel analysis">
      <h2>제품 분석</h2>

      <div className="analysis-highlight">
        <span className="analysis-highlight-tag">핵심 가치제안</span>
        <p>{analysis.core_value_proposition || '분석된 내용이 없습니다.'}</p>
      </div>

      <div className="analysis-grid">
        <AnalysisList title="예상 구매동기" items={analysis.expected_purchase_motivations} />
        <AnalysisList title="예상 저항요소" items={analysis.expected_resistance_factors} />
        <AnalysisList title="주요 비교대상" items={analysis.main_competitors_or_alternatives} />
        <AnalysisList title="카피의 강점" items={analysis.copy_strengths} />
        <AnalysisList title="카피의 약점" items={analysis.copy_weaknesses} />
      </div>

      <div className="analysis-highlight analysis-highlight--fit">
        <span className="analysis-highlight-tag">타겟 적합도 요약</span>
        <p>{analysis.target_fit_summary || '분석된 내용이 없습니다.'}</p>
      </div>
    </div>
  );
}

export default ProductAnalysisCard;
