<template>
  <router-view />
</template>

<script setup>
</script>

<style>
:root {
  color-scheme: light;

  /* === Color Tokens (OKLCH with sRGB fallbacks) === */
  /* Brand accent - warm teal/green hue ~170 */
  --color-accent: #0d9488;
  --color-accent: oklch(0.55 0.14 170);
  --color-accent-hover: #0f766e;
  --color-accent-hover: oklch(0.48 0.14 170);
  --color-accent-active: #115e59;
  --color-accent-active: oklch(0.42 0.14 170);
  --color-accent-subtle: #e6f7f5;
  --color-accent-subtle: oklch(0.94 0.03 170);
  --color-accent-muted: #ccefea;
  --color-accent-muted: oklch(0.88 0.04 170);

  /* Navbar */
  --color-navbar-bg: #1a2e2b;
  --color-navbar-bg: oklch(0.22 0.01 170);

  /* Neutrals - tinted with tiny chroma toward brand hue */
  --color-bg: #fafcfb;
  --color-bg: oklch(0.985 0.005 170);
  --color-surface: #f3f7f6;
  --color-surface: oklch(0.97 0.005 170);
  --color-surface-raised: #f9fcfb;
  --color-surface-raised: oklch(0.99 0.005 170);
  --color-border: #d5dfdd;
  --color-border: oklch(0.88 0.008 170);
  --color-border-muted: #e2eae8;
  --color-border-muted: oklch(0.92 0.006 170);
  --color-text: #1a2e2b;
  --color-text: oklch(0.2 0.01 170);
  --color-text-secondary: #4a6560;
  --color-text-secondary: oklch(0.4 0.008 170);
  --color-text-muted: #6e8a85;
  --color-text-muted: oklch(0.55 0.006 170);
  --color-text-on-accent: #f9fcfb;
  --color-text-on-accent: oklch(0.98 0.005 170);

  /* Semantic colors */
  --color-success: #22c55e;
  --color-success: oklch(0.6 0.15 145);
  --color-warning: #ca8a04;
  --color-warning: oklch(0.7 0.12 75);
  --color-error: #dc2626;
  --color-error: oklch(0.55 0.2 25);
  --color-error-bg: #fef2f2;
  --color-error-bg: oklch(0.95 0.03 25);

  /* === Typography === */
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  --font-mono: ui-monospace, 'SF Mono', 'Cascadia Code', 'Segoe UI Mono', monospace;

  /* Type scale (ratio ~1.15) */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.15rem;
  --text-xl: 1.325rem;
  --text-2xl: 1.75rem;
  --text-3xl: 2.25rem;

  --leading-tight: 1.25;
  --leading-normal: 1.6;
  --leading-relaxed: 1.75;

  /* === Spacing (4pt scale) === */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
  --space-12: 48px;
  --space-16: 64px;
  --space-24: 96px;

  /* === Radius === */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;

  /* === Shadows === */
  --shadow-sm: 0 1px 2px rgba(26, 46, 43, 0.05);
  --shadow-sm: 0 1px 2px oklch(0.2 0.01 170 / 0.05);
  --shadow-md: 0 2px 8px rgba(26, 46, 43, 0.08);
  --shadow-md: 0 2px 8px oklch(0.2 0.01 170 / 0.08);

  /* === Transitions === */
  --duration-fast: 150ms;
  --duration-normal: 200ms;
  --duration-slow: 250ms;
  --ease: cubic-bezier(0.4, 0, 0.2, 1);

  /* === Focus ring === */
  --focus-ring: 0 0 0 2px var(--color-bg), 0 0 0 4px var(--color-accent);

  /* === Layout === */
  --content-width: 70ch;
  --page-width: 1200px;
}

*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  font-family: var(--font-sans);
  color: var(--color-text);
  background: var(--color-bg);
  line-height: var(--leading-normal);
  min-height: 100vh;
}

a {
  color: inherit;
  text-decoration: none;
}

button {
  font-family: inherit;
  cursor: pointer;
  border: none;
  background: none;
}

input,
textarea {
  font-family: inherit;
}

:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}

::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--color-surface);
}

::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: var(--radius-full);
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-muted);
}
</style>
