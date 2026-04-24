'use client';

import { useEffect, useRef, useState } from 'react';

import { useRunTestCaseAiAgent } from '@/app/(app)/(agent)/_hooks/use-run-test-case-ai-agent';
import { isErrorApiResult } from '@/utils/api';

export const STAGES = [
  { label: 'Reading conversation transcript…', duration: 2000 },
  { label: 'Reading agent prompt…', duration: 2200 },
  { label: 'Analysing existing test cases…', duration: 3000 },
  { label: 'Generating persona and scenario…', duration: 3600 },
  { label: 'Building expected outcomes…', duration: 2600 },
  { label: 'Finalising test case…', duration: 1600 },
];

const TICK_MS = 30;
const HOLD_PROGRESS_AT = 95;
const COMPLETION_DELAY_MS = 200;

type Phase = 'input' | 'generating';

interface UseCreateTestCaseAiPromptArgs {
  agentId: string;
  onClose: () => void;
  onGenerated: (testCaseId: string) => void;
}

export function useCreateTestCaseAiPrompt({
  agentId,
  onClose,
  onGenerated,
}: UseCreateTestCaseAiPromptArgs) {
  const [phase, setPhase] = useState<Phase>('input');
  const [userPrompt, setUserPrompt] = useState('');
  const [stageIndex, setStageIndex] = useState(0);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const frameRef = useRef<number | null>(null);

  const { mutateAsync, isPending } = useRunTestCaseAiAgent(agentId);

  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  useEffect(() => {
    return () => {
      if (frameRef.current !== null) cancelAnimationFrame(frameRef.current);
    };
  }, []);

  const startStageAnimation = () => {
    setStageIndex(0);
    setProgress(0);
    let elapsed = 0;
    const total = STAGES.reduce((s, st) => s + st.duration, 0);
    const lastStageIndex = STAGES.length - 1;

    const runStage = (idx: number) => {
      const stage = STAGES[idx];
      if (!stage) return;
      setStageIndex(idx);
      const end = elapsed + stage.duration;

      const tick = () => {
        elapsed += TICK_MS;
        const computed = Math.min(100, Math.round((elapsed / total) * 100));
        setProgress(idx === lastStageIndex ? Math.min(HOLD_PROGRESS_AT, computed) : computed);
        if (elapsed < end) {
          frameRef.current = requestAnimationFrame(tick);
        } else {
          elapsed = end;
          if (idx < lastStageIndex) {
            runStage(idx + 1);
          } else {
            setProgress(HOLD_PROGRESS_AT);
            frameRef.current = null;
          }
        }
      };
      frameRef.current = requestAnimationFrame(tick);
    };

    runStage(0);
  };

  const cancelAnimation = () => {
    if (frameRef.current !== null) cancelAnimationFrame(frameRef.current);
    frameRef.current = null;
  };

  const handleGenerate = async () => {
    const prompt = userPrompt.trim();
    if (!prompt) return;
    setError(null);
    setPhase('generating');
    startStageAnimation();

    const result = await mutateAsync({ prompt });
    cancelAnimation();

    if (isErrorApiResult(result)) {
      setPhase('input');
      setStageIndex(0);
      setProgress(0);
      setError('AI generation failed. Try again.');
      return;
    }

    setProgress(100);

    const created = result.data?.created?.[0] ?? result.data?.edited ?? null;
    setTimeout(() => {
      if (created?.id) {
        onGenerated(created.id);
      } else {
        onClose();
      }
    }, COMPLETION_DELAY_MS);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      void handleGenerate();
    }
  };

  return {
    phase,
    userPrompt,
    setUserPrompt,
    stageIndex,
    progress,
    error,
    textareaRef,
    isPending,
    handleGenerate,
    handleKeyDown,
  };
}
