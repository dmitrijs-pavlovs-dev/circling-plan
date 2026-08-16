const puppeteer = require('puppeteer-core');
const fs = require('fs');

const PAGE = 'file:///Users/dmitrijs/apps/circling-plan/video/countdown.html';
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

function arg(name, fallback) {
  const i = process.argv.indexOf(name);
  return i === -1 ? fallback : process.argv[i + 1];
}

(async () => {
  const test = process.argv.includes('--test');
  const out = arg('--out', '/tmp/render/frames');
  const phasesFile = arg('--phases', null);

  let phases = null, duration = 5146;
  if (phasesFile) {
    const j = JSON.parse(fs.readFileSync(phasesFile, 'utf8'));
    phases = j.phases;
    duration = j.duration;
  }

  fs.mkdirSync(out, { recursive: true });
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: 'new',
    args: ['--force-device-scale-factor=1', '--hide-scrollbars'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  await page.goto(PAGE, { waitUntil: 'networkidle0' });
  await page.evaluate(() => document.fonts.ready);
  if (phases) {
    await page.evaluate((p, d) => window.setPhases(p, d), phases, duration);
  }

  const total = Math.ceil(duration);
  const times = test
    ? [0, Math.round(total * 0.2), Math.round(total * 0.5), Math.round(total * 0.85)]
        .map((t, i) => ({ t, name: `test-${i}` }))
    : Array.from({ length: total }, (_, i) => ({ t: i, name: String(i).padStart(5, '0') }));

  let n = 0;
  for (const { t, name } of times) {
    await page.evaluate((tt) => window.seek(tt), t);
    await page.screenshot({ path: `${out}/${name}.jpg`, type: 'jpeg', quality: 90 });
    if (++n % 250 === 0) console.log(`rendered ${n}/${times.length}`);
  }
  console.log(`done: ${n} frames -> ${out}`);
  await browser.close();
})();
