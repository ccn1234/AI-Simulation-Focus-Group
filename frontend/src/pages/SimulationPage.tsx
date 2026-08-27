import { useState } from 'react';
import SimulationForm from '../components/SimulationForm';
import ProductAnalysisCard from '../components/ProductAnalysisCard';
import SummaryReportCard from '../components/SummaryReportCard';
import DiscussionCard from '../components/DiscussionCard';
import PersonaCard from '../components/PersonaCard';
import ExecutiveSummary from '../components/ExecutiveSummary';
import WorkflowSteps from '../components/WorkflowSteps';
import { useSimulation } from '../hooks/useSimulation';
import type { SimulationStatus } from '../types/simulation';

const STATUS_COPY: Record<SimulationStatus, { label: string; title: string; description: string }> = {
  pending: {
    label: '대기 중',
    title: '시뮬레이션 작업이 등록되었습니다.',
    description: 'AI 포커스 그룹을 준비하고 있습니다. 잠시만 기다려 주세요.',
  },
  running: {
    label: '분석 중',
    title: 'AI 포커스 그룹이 분석하고 있습니다.',
    description: '제품 분석 → 페르소나 생성 → 소비자 반응 → Moderator 리포트 → 그룹 토론 순서로 처리됩니다.',
  },
  succeeded: {
    label: '완료',
    title: '시뮬레이션이 완료되었습니다.',
    description: 'AI 포커스 그룹의 분석 결과가 아래에 표시됩니다.',
  },
  failed: {
    label: '실패',
    title: '시뮬레이션 작업을 완료하지 못했습니다.',
    description: '표시된 오류 내용을 확인한 뒤 다시 시도해 주세요.',
  },
};

function SimulationPage() {
  const [productName, setProductName] = useState('AI 영어 회화 앱');
  const [productDescription, setProductDescription] = useState('매일 10분씩 AI와 영어 회화를 할 수 있는 앱입니다. 초보자를 위한 음성 피드백을 제공합니다.');
  const [targetAudience, setTargetAudience] = useState('20~30대 직장인');
  const [adCopy, setAdCopy] = useState('퇴근길 10분, 영어가 습관이 됩니다.');
  const { result, loading, error, status, simulationId, submit } = useSimulation();
  const handleSubmit = () => submit({ product_name: productName, product_description: productDescription, target_audience: targetAudience, ad_copy: adCopy });
  const getPersona = (id: number) => result?.personas.find((persona) => persona.id === id);
  const statusCopy = status ? STATUS_COPY[status] : null;

  return <main className="container">
    <section className="intro-layout"><div className="hero"><p className="eyebrow">AI Simulation Focus Group</p><h1>출시 전에,<br /><span>소비자의 반응</span>을 확인하세요.</h1><p className="subtitle">제품과 광고 카피를 입력하면 AI 소비자 10명이 제품을 평가하고, 구매 장벽과 다음 액션을 리포트로 정리합니다.</p><div className="hero-proof"><span>10</span><p>가상 소비자<br /><small>다양한 관점의 반응</small></p><span>4</span><p>단계 분석<br /><small>제품부터 토론까지</small></p></div></div><SimulationForm productName={productName} onProductNameChange={setProductName} productDescription={productDescription} onProductDescriptionChange={setProductDescription} targetAudience={targetAudience} onTargetAudienceChange={setTargetAudience} adCopy={adCopy} onAdCopyChange={setAdCopy} loading={loading} error={error} onSubmit={handleSubmit} /></section>
    {!result && !loading && <WorkflowSteps />}
    {loading && !status && <section className="panel simulation-status simulation-status--pending" role="status" aria-live="polite"><div className="simulation-status__meta"><span>요청 중</span></div><strong>시뮬레이션 작업을 등록하고 있습니다.</strong><p>서버에 입력 내용을 안전하게 전달하고 있습니다.</p><div className="loading-bar"><span /></div></section>}
    {statusCopy && simulationId !== null && (!error || status === 'failed') && <section className={`panel simulation-status simulation-status--${status}`} role={status === 'failed' ? 'alert' : 'status'} aria-live="polite"><div className="simulation-status__meta"><span>{statusCopy.label}</span><small>작업 #{simulationId}</small></div><strong>{statusCopy.title}</strong><p>{statusCopy.description}</p>{(status === 'pending' || status === 'running') && <div className="loading-bar"><span /></div>}</section>}
    {result && <section className="results"><ExecutiveSummary report={result.summary_report} responses={result.responses} /><ProductAnalysisCard analysis={result.product_analysis} /><details className="result-details" open><summary>전체 Moderator 리포트 보기</summary><SummaryReportCard report={result.summary_report} /></details><details className="result-details"><summary>AI 그룹 토론 보기</summary><DiscussionCard discussion={result.discussion_result} /></details><details className="result-details"><summary>10명 페르소나별 반응 보기</summary><h2 className="section-heading">페르소나별 반응</h2>{result.responses?.length ? <div className="card-grid">{result.responses.map((response) => <PersonaCard key={response.persona_id} persona={getPersona(response.persona_id)} response={response} />)}</div> : <p className="meta empty-fallback">표시할 페르소나 응답이 없습니다.</p>}</details></section>}
  </main>;
}

export default SimulationPage;
