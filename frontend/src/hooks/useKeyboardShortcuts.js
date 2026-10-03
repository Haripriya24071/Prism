import { useEffect } from 'react';

export function useKeyboardShortcuts(shortcuts = {}) {
  useEffect(() => {
    function handleKeyDown(e) {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

      const keyCombo = [
        e.ctrlKey ? 'ctrl' : '',
        e.shiftKey ? 'shift' : '',
        e.key.toLowerCase(),
      ].filter(Boolean).join('+');

      if (shortcuts[keyCombo]) {
        e.preventDefault();
        shortcuts[keyCombo]();
      }
    }

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [shortcuts]);
}
