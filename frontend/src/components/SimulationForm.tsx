type SimulationFormProps = {
  productName: string;
  onProductNameChange: (value: string) => void;
  productDescription: string;
  onProductDescriptionChange: (value: string) => void;
  targetAudience: string;
  onTargetAudienceChange: (value: string) => void;
  adCopy: string;
  onAdCopyChange: (value: string) => void;
  loading: boolean;
  error: string;
  onSubmit: () => void;
};

function SimulationForm({
  productName,
  onProductNameChange,
  productDescription,
  onProductDescriptionChange,
  targetAudience,
  onTargetAudienceChange,
  adCopy,
  onAdCopyChange,
  loading,
  error,
  onSubmit,
}: SimulationFormProps) {
  return (
    <section className="panel form-panel">
      <label>
        제품명
        <input value={productName} onChange={(e) => onProductNameChange(e.target.value)} />
      </label>

      <label>
        제품 설명
        <textarea value={productDescription} onChange={(e) => onProductDescriptionChange(e.target.value)} rows={5} />
      </label>

      <label>
        타겟 고객
        <input value={targetAudience} onChange={(e) => onTargetAudienceChange(e.target.value)} />
      </label>

      <label>
        광고 카피
        <textarea value={adCopy} onChange={(e) => onAdCopyChange(e.target.value)} rows={3} />
      </label>

      <button onClick={onSubmit} disabled={loading}>
        {loading ? '시뮬레이션 중...' : '시뮬레이션 시작'}
      </button>

      {error && (
        <div className="error-state" role="alert">
          <strong>시뮬레이션을 실행하지 못했습니다.</strong>
          <p>{error}</p>
          <small>입력값을 확인한 뒤 다시 시도해 주세요.</small>
        </div>
      )}
    </section>
  );
}

export default SimulationForm;
