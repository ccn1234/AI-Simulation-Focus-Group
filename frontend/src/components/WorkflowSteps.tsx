const steps = [
  ['01', '제품 입력', '제품 설명과 광고 카피를 입력합니다.'],
  ['02', '페르소나 생성', '서로 다른 10명의 소비자를 구성합니다.'],
  ['03', '그룹 토론', '소비자 반응과 의견 충돌을 시뮬레이션합니다.'],
  ['04', '인사이트 리포트', '구매 장벽과 다음 액션을 확인합니다.'],
];

export default function WorkflowSteps() {
  return <section className="workflow-section" aria-labelledby="workflow-title"><div className="workflow-heading"><p className="eyebrow">How it works</p><h2 id="workflow-title">아이디어가 인사이트가 되는 과정</h2></div><div className="workflow-grid">{steps.map(([number, title, description]) => <article className="workflow-step" key={number}><span>{number}</span><h3>{title}</h3><p>{description}</p></article>)}</div></section>;
}
