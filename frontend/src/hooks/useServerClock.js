import { useState, useEffect } from 'react';

export function useServerClock(serverTimeStr, initialMinutesRemaining) {
  const [minutesRemaining, setMinutesRemaining] = useState(initialMinutesRemaining);
  const [secondsRemaining, setSecondsRemaining] = useState(0);

  useEffect(() => {
    setMinutesRemaining(initialMinutesRemaining);
    setSecondsRemaining(0);
  }, [initialMinutesRemaining, serverTimeStr]);

  useEffect(() => {
    if (minutesRemaining === null || minutesRemaining === undefined || minutesRemaining <= 0) {
      return;
    }

    const timer = setInterval(() => {
      setSecondsRemaining((prevSec) => {
        if (prevSec <= 0) {
          setMinutesRemaining((prevMin) => (prevMin > 0 ? prevMin - 1 : 0));
          return 59;
        }
        return prevSec - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [minutesRemaining]);

  const formattedCountdown = minutesRemaining != null
    ? `${minutesRemaining} min ${secondsRemaining > 0 ? `${secondsRemaining}s` : ''}`
    : '--';

  return {
    minutesRemaining,
    secondsRemaining,
    formattedCountdown,
  };
}
