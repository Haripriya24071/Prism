import { useEffect } from 'react';

/**
 * Browser default shortcuts that are strictly protected and MUST NEVER be intercepted.
 * Intercepting these would break essential OS and browser functionality
 * (saving, clipboard, page reloading, tab management).
 */
export const PROTECTED_BROWSER_SHORTCUTS = Object.freeze([
  'ctrl+s',        // Browser Save webpage / file
  'ctrl+c',        // System Clipboard Copy
  'ctrl+v',        // System Clipboard Paste
  'ctrl+r',        // Browser Page Reload
  'ctrl+w',        // Browser Close Tab/Window
  'f5',            // Browser Refresh
  'ctrl+shift+r',  // Browser Hard Reload
]);

/**
 * Application shortcuts registered for PRISM.
 * Each shortcut is documented with its action and safety rationale.
 */
export const DEFAULT_SHORTCUTS = Object.freeze({
  /**
   * Escape: Closes open modal dialogs, flyout drawers, or expanded menus.
   * Why it's safe: Follows W3C WAI-ARIA standards for keyboard accessibility;
   * does not conflict with browser navigation or system shortcuts.
   */
  escape: () => {
    const activeOverlay = document.querySelector('[role="dialog"], [aria-modal="true"], aside[aria-label]');
    if (activeOverlay && typeof activeOverlay.close === 'function') {
      activeOverlay.close();
    }
  },

  /**
   * Shift + ?: Triggers shortcut help / tips reference.
   * Why it's safe: Industry-standard convention (GitHub, Gmail, Slack) for non-destructive
   * help discoverability; ignored when typing in form inputs.
   */
  'shift+?': () => {
    const helpBtn = document.querySelector('[data-shortcut-help]');
    if (helpBtn) helpBtn.click();
  },

  /**
   * Alt + 1: Navigates to the Idea Intake input section.
   * Why it's safe: Uses the Alt modifier (standard accesskey convention) rather than Ctrl
   * to avoid colliding with browser tab/window shortcuts.
   */
  'alt+1': () => {
    const target = document.getElementById('pitch-terminal') || document.querySelector('main');
    if (target) target.scrollIntoView({ behavior: 'smooth' });
  },

  /**
   * Alt + 2: Navigates to the Swarm / Agent grid view.
   * Why it's safe: Uses Alt modifier instead of Ctrl+2 (which switches browser tabs in Chrome/Firefox).
   */
  'alt+2': () => {
    const target = document.getElementById('swarm-heading') || document.querySelector('.agent-grid');
    if (target) target.scrollIntoView({ behavior: 'smooth' });
  },

  /**
   * Alt + 3: Navigates to the Results / BRD viewer section.
   * Why it's safe: Uses Alt modifier instead of Ctrl+R (which reloads the page) to safely inspect requirements.
   */
  'alt+3': () => {
    const target = document.querySelector('.score-card') || document.querySelector('.brd-viewer');
    if (target) target.scrollIntoView({ behavior: 'smooth' });
  },
});

export function useKeyboardShortcuts(customShortcuts = {}) {
  useEffect(() => {
    function handleKeyDown(e) {
      // Do not intercept keystrokes while the user is focused in text inputs
      if (
        e.target.tagName === 'INPUT' ||
        e.target.tagName === 'TEXTAREA' ||
        e.target.isContentEditable
      ) {
        return;
      }

      const keyCombo = [
        (e.ctrlKey || e.metaKey) ? 'ctrl' : '',
        e.altKey ? 'alt' : '',
        e.shiftKey ? 'shift' : '',
        e.key.toLowerCase(),
      ].filter(Boolean).join('+');

      // Confirm none conflict with browser defaults; never intercept protected shortcuts
      if (PROTECTED_BROWSER_SHORTCUTS.includes(keyCombo)) {
        return;
      }

      const activeShortcuts = { ...DEFAULT_SHORTCUTS, ...customShortcuts };

      if (activeShortcuts[keyCombo]) {
        e.preventDefault();
        activeShortcuts[keyCombo](e);
      }
    }

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [customShortcuts]);
}
