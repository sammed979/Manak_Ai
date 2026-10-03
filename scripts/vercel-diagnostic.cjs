#!/usr/bin/env node
// Mirror of the diagnostic placed at repo root so it works whether
// Vercel's Root Directory is blank or `frontend`.
const { writeFileSync, mkdirSync, existsSync } = require('node:fs');
const path = require('node:path');

const cwd = process.cwd();
const nodeVer = process.version;
const npmVer  = process.env.npm_config_user_agent || '';
const rootDir = process.env.VERCEL_URL ? 'VERCEL=' + process.env.VERCEL_URL : 'local';

function exists(p) { try { return existsSync(p); } catch { return false; } }

const hasPkgAtCwd        = exists('package.json');
const hasFrontendPkg     = exists(path.join(cwd, 'frontend/package.json'));
const hasFrontendVercel  = exists(path.join(cwd, 'frontend/vercel.json'));
const hasRootVercel      = exists(path.join(cwd, 'vercel.json'));

const sep = '—'.repeat(78);
console.log('\n' + sep);
console.log('🔍 MANAK-AI VERCEL BUILD DIAGNOSTIC (ROOT)');
console.log(sep);
console.log('  process.cwd()        :', cwd);
console.log('  Node.js version      :', nodeVer);
console.log('  npm user agent       :', npmVer);
console.log('  VERCEL_URL tag       :', rootDir);
console.log('  package.json @ cwd   :', hasPkgAtCwd        ? 'YES' : 'NO');
console.log('  vercel.json @ cwd    :', hasRootVercel      ? 'YES' : 'NO');
console.log('  frontend/package.json:', hasFrontendPkg    ? 'YES' : 'NO');
console.log('  frontend/vercel.json :', hasFrontendVercel ? 'YES' : 'NO');
console.log(sep);

let verdict = 'UNKNOWN';
if (hasPkgAtCwd && exists('frontend/package.json')) {
  verdict = 'ROOT DIRECTORY = project-root (✅ correct; use ./vercel.json with cd frontend && commands)';
} else if (hasPkgAtCwd && !hasFrontendPkg) {
  const pkg = require(path.join(cwd, 'package.json'));
  if (pkg && pkg.name === 'manak-ai-frontend') {
    verdict = 'ROOT DIRECTORY = "frontend" subfolder (✅ correct for frontend/vercel.json directly)';
  } else {
    verdict = 'WARN ⚠️ package.json found at cwd but it is NOT the frontend package, and no frontend/ subfolder.';
  }
} else if (!hasPkgAtCwd) {
  verdict = 'FATAL ❌ NO package.json at cwd. Repository not checked out properly, or Root Dir wrong.';
}
console.log('📍 EXPECTED CONFIG     :', verdict);
console.log(sep + '\n');

try {
  mkdirSync(path.resolve(cwd, '.manak-diagnostic'), { recursive: true });
  writeFileSync(
    path.resolve(cwd, '.manak-diagnostic', 'build-context.json'),
    JSON.stringify({ cwd, nodeVer, verdict, hasPkgAtCwd, hasFrontendPkg, hasRootVercel, hasFrontendVercel }, null, 2)
  );
} catch (_) { /* non-fatal */ }

if (verdict.startsWith('FATAL')) process.exit(1);
