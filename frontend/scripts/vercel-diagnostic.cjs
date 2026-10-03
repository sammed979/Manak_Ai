#!/usr/bin/env node
// Vercel build diagnostic. Prints the state Vercel is actually running in
// BEFORE npm install/build runs, so we can misconfig instantly.
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
const hasDistAtCwd       = exists('dist');
const hasFrontendDist    = exists(path.join(cwd, 'frontend/dist'));

const sep = '—'.repeat(78);
console.log('\n' + sep);
console.log('🔍 MANAK-AI VERCEL BUILD DIAGNOSTIC');
console.log(sep);
console.log('  process.cwd()        :', cwd);
console.log('  Node.js version      :', nodeVer);
console.log('  npm user agent       :', npmVer);
console.log('  VERCEL_URL tag       :', rootDir);
console.log('  package.json @ cwd   :', hasPkgAtCwd        ? 'YES ✅' : 'NO  ⚠️');
console.log('  vercel.json @ cwd    :', hasRootVercel      ? 'YES'    : 'NO');
console.log('  frontend/package.json:', hasFrontendPkg    ? 'YES'    : 'NO');
console.log('  frontend/vercel.json :', hasFrontendVercel ? 'YES'    : 'NO');
console.log('  dist/       @ cwd    :', hasDistAtCwd       ? 'PRE-EXISTS (cache)' : '—');
console.log('  frontend/dist/       :', hasFrontendDist    ? 'PRE-EXISTS (cache)' : '—');
console.log(sep);

// Decide expected configuration
let verdict = 'UNKNOWN';
if (hasPkgAtCwd && /"name":\s*"manak-ai-frontend"/.test(require('node:fs').readFileSync('package.json','utf8'))) {
  verdict = 'ROOT DIRECTORY = "frontend" (✅ correct for frontend/vercel.json)';
} else if (hasFrontendPkg && !hasPkgAtCwd) {
  verdict = 'ROOT DIRECTORY = project-root (✅ correct for root-level vercel.json → cd frontend && …)';
} else if (!hasPkgAtCwd && !hasFrontendPkg) {
  verdict = 'FATAL ❌ NO package.json FOUND ANYWHERE. Check out the git repo first.';
} else {
  verdict = 'WARN ⚠️ Ambiguous — both a root package.json AND frontend/package.json were detected.';
}
console.log('📍 EXPECTED CONFIG     :', verdict);
console.log(sep + '\n');

// Also write the verdict to the output as a marker file so weird edge cases are easier to grep
try {
  mkdirSync(path.resolve(cwd, '.manak-diagnostic'), { recursive: true });
  writeFileSync(
    path.resolve(cwd, '.manak-diagnostic', 'build-context.json'),
    JSON.stringify({ cwd, nodeVer, verdict, hasPkgAtCwd, hasFrontendPkg, hasRootVercel, hasFrontendVercel }, null, 2)
  );
} catch (_) { /* non-fatal */ }

if (verdict.startsWith('FATAL')) process.exit(1);
