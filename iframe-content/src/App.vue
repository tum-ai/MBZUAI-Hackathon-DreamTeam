
<template>
  <router-view/>
</template>


<style>
/* --- Global Styles from project.json --- */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');

body {
  font-family: 'Inter', sans-serif;
  background-color: #000;
  color: #fff;
  margin: 0;
  padding: 0;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* V18: Removed hardcoded #nav styles, now part of AST */

.page-container {
  max-width: 100%; /* Full width for hero sections */
  margin: 0 auto;
}

.content-width {
  max-width: 980px;
  margin: 0 auto;
  padding: 2rem;
}

h1, h2, h3, h4 {
  font-weight: 700;
  margin: 0;
  padding: 0;
}

/* --- Global Component Classes --- */
.btn-primary {
  background-color: #007aff;
  color: white;
  border: none;
  padding: 10px 20px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 99px; /* Pill shape */
  cursor: pointer;
  transition: background-color 0.2s;
  text-decoration: none;
}
.btn-primary:hover {
  background-color: #0056b3;
}
/* V18: Added secondary button for pricing toggle */
.btn-secondary {
  background-color: #333;
  color: #fff;
  border: 1px solid #555;
  padding: 10px 20px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 99px;
  cursor: pointer;
  transition: background-color 0.2s;
}
.btn-secondary:hover {
  background-color: #444;
}

.text-link {
  color: #007aff;
  text-decoration: none;
}
.text-link:hover {
  text-decoration: underline;
}

.icon-check {
  color: #34c759; /* Apple green */
  width: 1.5em;
  height: 1.5em;
  margin-right: 0.5rem;
}

.icon-chevron {
  width: 0.8em;
  height: 0.8em;
  margin-left: 0.25rem;
}

/* --- End Global Styles --- */


/* --- V20: Animations for Advanced Components --- */
@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
/* --- End Animations --- */

</style>

