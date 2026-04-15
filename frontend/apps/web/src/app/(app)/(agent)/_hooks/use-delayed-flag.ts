import { useEffect, useRef, useState } from 'react';

/**
 * Returns `true` while `flag` is true, and stays true for an extra
 * `delay` ms after `flag` goes false — useful for keeping spinners
 * visible long enough to be perceived.
 */
export function useDelayedFlag(flag: boolean, delay = 300): boolean {
  const [visible, setVisible] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const prevFlagRef = useRef(flag);

  // Synchronously show when flag turns on (no effect needed)
  if (flag && !prevFlagRef.current) {
    setVisible(true);
  }
  prevFlagRef.current = flag;

  // Delay hiding when flag turns off
  useEffect(() => {
    if (!flag) {
      timerRef.current = setTimeout(() => setVisible(false), delay);
      return () => {
        if (timerRef.current) clearTimeout(timerRef.current);
      };
    }
  }, [flag, delay]);

  return visible;
}
