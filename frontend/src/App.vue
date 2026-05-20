<template>
  <router-view />
</template>

<script setup>
</script>

<style>
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
  font-family: 'JetBrains Mono', 'Space Grotesk', 'Inter', 'Noto Sans SC', monospace;
  color: #000;
  background: #fff;
  line-height: 1.6;
  min-height: 100vh;
}

a {
  color: inherit;
  text-decoration: none;
}

button {
  font-family: inherit;
  cursor: pointer;
}

input,
textarea {
  font-family: inherit;
}

::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f0f0f0;
}

::-webkit-scrollbar-thumb {
  background: #000;
  border-radius: 0;
}

::-webkit-scrollbar-thumb:hover {
  background: #FF4500;
}
</style>
