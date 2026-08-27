import { useEffect, useRef, useState } from 'react';
import { createSimulationJob, getSimulationStatus } from '../services/simulationApi';
import type {
  SimulationRequestPayload,
  SimulationResult,
  SimulationStatus,
  SimulationStatusResponse,
} from '../types/simulation';

const POLL_INTERVAL_MS = 2_000;

function waitForNextPoll(milliseconds: number, signal: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    if (signal.aborted) {
      reject(new DOMException('Polling aborted', 'AbortError'));
      return;
    }

    const timeoutId = window.setTimeout(() => {
      signal.removeEventListener('abort', abort);
      resolve();
    }, milliseconds);

    function abort() {
      window.clearTimeout(timeoutId);
      reject(new DOMException('Polling aborted', 'AbortError'));
    }

    signal.addEventListener('abort', abort, { once: true });
  });
}

function toSimulationResult(status: SimulationStatusResponse): SimulationResult {
  if (
    !status.product_analysis ||
    !status.summary_report ||
    !status.discussion_result
  ) {
    throw new Error('완료된 시뮬레이션의 결과 데이터가 누락되었습니다.');
  }

  return {
    product_analysis: status.product_analysis,
    personas: status.personas,
    responses: status.responses,
    summary_report: status.summary_report,
    discussion_result: status.discussion_result,
  };
}

export function useSimulation() {
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [status, setStatus] = useState<SimulationStatus | null>(null);
  const [simulationId, setSimulationId] = useState<number | null>(null);
  const activeRequest = useRef<AbortController | null>(null);

  useEffect(() => {
    return () => {
      const controller = activeRequest.current;
      activeRequest.current = null;
      controller?.abort();
    };
  }, []);

  const submit = async (payload: SimulationRequestPayload) => {
    activeRequest.current?.abort();
    const controller = new AbortController();
    activeRequest.current = controller;

    setLoading(true);
    setError('');
    setResult(null);
    setStatus(null);
    setSimulationId(null);

    try {
      const job = await createSimulationJob(payload, controller.signal);
      setSimulationId(job.id);
      setStatus(job.status);

      while (!controller.signal.aborted) {
        const current = await getSimulationStatus(job.id, controller.signal);
        setStatus(current.status);

        if (current.status === 'succeeded') {
          setResult(toSimulationResult(current));
          return;
        }

        if (current.status === 'failed') {
          throw new Error(current.error_message || '시뮬레이션 실행에 실패했습니다.');
        }

        await waitForNextPoll(POLL_INTERVAL_MS, controller.signal);
      }
    } catch (err) {
      if (!(err instanceof Error && err.name === 'AbortError')) {
        setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
      }
    } finally {
      if (activeRequest.current === controller) {
        activeRequest.current = null;
        setLoading(false);
      }
    }
  };

  return { result, loading, error, status, simulationId, submit };
}
