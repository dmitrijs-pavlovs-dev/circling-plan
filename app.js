/* ---------- Config ---------- */
const MARKDOWN_FILE = 'session-program-v2.md';
const DEFAULT_VIDEO_ID = 'JpWHmFQvNR8'; // Nicola Cruz – Cumbia del Olvido (ZZK Records)

/* ---------- Helpers ---------- */
const $ = (sel) => document.querySelector(sel);
const pad = (n) => String(n).padStart(2, '0');
function slugify(text) {
  return text.toLowerCase().trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-');
}
function fmtTime(sec) {
  sec = Math.max(0, Math.floor(sec || 0));
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}:${pad(s)}`;
}

/* ---------- Render markdown ---------- */
async function loadContent() {
  const content = $('#content');
  try {
    const res = await fetch(MARKDOWN_FILE, { cache: 'no-store' });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const md = await res.text();
    marked.setOptions({ gfm: true, breaks: false });
    content.innerHTML = marked.parse(md);

    // Heading anchors
    content.querySelectorAll('h1, h2, h3').forEach((h) => {
      if (!h.id) h.id = slugify(h.textContent);
    });
    // Wrap tables for horizontal scroll
    content.querySelectorAll('table').forEach((t) => {
      const wrap = document.createElement('div');
      wrap.className = 'table-wrap';
      t.parentNode.insertBefore(wrap, t);
      wrap.appendChild(t);
    });
    buildTOC(content);
  } catch (err) {
    content.innerHTML = `<p class="loading">Could not load the plan (${err.message}).</p>`;
  }
}

function buildTOC(content) {
  const toc = $('#toc');
  const heads = content.querySelectorAll('h2');
  toc.innerHTML = '';
  heads.forEach((h) => {
    const a = document.createElement('a');
    a.href = '#' + h.id;
    a.textContent = h.textContent.replace(/[✅🎵♪].*$/u, '').trim();
    a.addEventListener('click', (e) => {
      e.preventDefault();
      document.getElementById(h.id).scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    toc.appendChild(a);
  });
}

/* ---------- Clock ---------- */
function startClock() {
  const el = $('#clock');
  const tick = () => {
    const d = new Date();
    el.textContent = `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
  };
  tick();
  setInterval(tick, 1000);
}

/* ---------- Focus Timer ---------- */
const Timer = (() => {
  let mode = 'countdown';      // 'countdown' | 'stopwatch'
  let presetSec = 15 * 60;
  let remaining = presetSec;   // countdown
  let elapsed = 0;             // stopwatch
  let running = false;
  let ticker = null;
  const display = $('#timerDisplay');

  function render() {
    const sec = mode === 'countdown' ? remaining : elapsed;
    display.textContent = fmtTime(sec);
    display.classList.toggle('warn', mode === 'countdown' && remaining <= 30 && remaining > 0 && running);
    display.classList.toggle('done', mode === 'countdown' && remaining === 0);
  }

  function tick() {
    if (mode === 'countdown') {
      remaining = Math.max(0, remaining - 1);
      if (remaining === 0) { stop(); alarm(); }
    } else {
      elapsed += 1;
    }
    render();
  }

  function start() {
    if (running) { pause(); return; }
    if (mode === 'countdown' && remaining === 0) remaining = presetSec;
    running = true;
    $('#timerStart').textContent = 'Pause';
    ticker = setInterval(tick, 1000);
  }
  function pause() {
    running = false;
    $('#timerStart').textContent = 'Start';
    clearInterval(ticker);
  }
  function stop() {
    running = false;
    $('#timerStart').textContent = 'Start';
    clearInterval(ticker);
  }
  function reset() {
    stop();
    remaining = presetSec;
    elapsed = 0;
    render();
  }
  function setPreset(min) {
    presetSec = min * 60;
    if (!running) remaining = presetSec;
    render();
  }
  function adjust(deltaMin) {
    presetSec = Math.max(60, presetSec + deltaMin * 60);
    if (!running || mode === 'countdown') remaining = presetSec;
    render();
  }
  function setMode(m) {
    mode = m;
    stop();
    if (m === 'countdown') remaining = presetSec; else elapsed = 0;
    render();
  }
  function alarm() {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      [0, 0.4, 0.8].forEach((t) => {
        const o = ctx.createOscillator(); const g = ctx.createGain();
        o.frequency.value = 660; o.connect(g); g.connect(ctx.destination);
        g.gain.setValueAtTime(0.0001, ctx.currentTime + t);
        g.gain.exponentialRampToValueAtTime(0.3, ctx.currentTime + t + 0.05);
        g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + t + 0.35);
        o.start(ctx.currentTime + t); o.stop(ctx.currentTime + t + 0.4);
      });
    } catch (e) {}
    if (navigator.vibrate) navigator.vibrate([300, 150, 300, 150, 300]);
  }

  function init() {
    $('#timerStart').addEventListener('click', start);
    $('#timerReset').addEventListener('click', reset);
    $('#plusMin').addEventListener('click', () => adjust(1));
    $('#minusMin').addEventListener('click', () => adjust(-1));
    $('#modeCountdown').addEventListener('click', () => {
      $('#modeCountdown').classList.add('active'); $('#modeStopwatch').classList.remove('active'); setMode('countdown');
    });
    $('#modeStopwatch').addEventListener('click', () => {
      $('#modeStopwatch').classList.add('active'); $('#modeCountdown').classList.remove('active'); setMode('stopwatch');
    });
    document.querySelectorAll('#presets .preset').forEach((b) => {
      b.addEventListener('click', () => {
        document.querySelectorAll('#presets .preset').forEach((x) => x.classList.remove('active'));
        b.classList.add('active');
        setPreset(parseInt(b.dataset.min, 10));
      });
    });
    render();
  }
  return { init };
})();

/* ---------- YouTube Player ---------- */
const Music = (() => {
  let player = null;
  let ready = false;
  let dragging = false;
  let poll = null;
  const seek = $('#seek');
  const curT = $('#curTime');
  const durT = $('#durTime');

  function parseId(input) {
    input = (input || '').trim();
    const m = input.match(/(?:v=|youtu\.be\/|embed\/|shorts\/)([A-Za-z0-9_-]{11})/);
    if (m) return m[1];
    if (/^[A-Za-z0-9_-]{11}$/.test(input)) return input;
    return null;
  }

  window.onYouTubeIframeAPIReady = function () {
    player = new YT.Player('player', {
      videoId: DEFAULT_VIDEO_ID,
      playerVars: { playsinline: 1, rel: 0, modestbranding: 1, controls: 1 },
      events: {
        onReady: () => { ready = true; player.setVolume(parseInt($('#vol').value, 10)); updateDuration(); },
        onStateChange: (e) => {
          if (e.data === YT.PlayerState.PLAYING) { $('#playBtn').textContent = '⏸ Pause'; startPoll(); updateDuration(); }
          else { $('#playBtn').textContent = '▶ Play'; }
          if (e.data === YT.PlayerState.ENDED) { $('#playBtn').textContent = '▶ Play'; }
        }
      }
    });
  };

  function updateDuration() {
    if (!ready) return;
    const d = player.getDuration();
    if (d > 0) { seek.max = d; durT.textContent = fmtTime(d); }
  }
  function startPoll() {
    clearInterval(poll);
    poll = setInterval(() => {
      if (!ready || dragging) return;
      const t = player.getCurrentTime();
      seek.value = t;
      curT.textContent = fmtTime(t);
    }, 250);
  }

  function init() {
    $('#playBtn').addEventListener('click', () => {
      if (!ready) return;
      const s = player.getPlayerState();
      if (s === YT.PlayerState.PLAYING) player.pauseVideo(); else player.playVideo();
    });
    $('#stopBtn').addEventListener('click', () => {
      if (!ready) return;
      player.pauseVideo(); player.seekTo(0, true);
      seek.value = 0; curT.textContent = '0:00';
    });
    seek.addEventListener('input', () => { dragging = true; curT.textContent = fmtTime(seek.value); });
    seek.addEventListener('change', () => {
      if (ready) player.seekTo(parseFloat(seek.value), true);
      dragging = false;
    });
    $('#vol').addEventListener('input', () => { if (ready) player.setVolume(parseInt($('#vol').value, 10)); });
    $('#ytLoad').addEventListener('click', () => {
      const id = parseId($('#ytInput').value);
      if (id && ready) {
        player.loadVideoById(id);
        $('#trackName').textContent = 'Loaded: ' + id;
      } else {
        $('#trackName').textContent = 'Could not read that link / ID';
      }
    });

    // Load IFrame API
    const tag = document.createElement('script');
    tag.src = 'https://www.youtube.com/iframe_api';
    document.head.appendChild(tag);
  }
  return { init };
})();

/* ---------- Dock / Panels ---------- */
function initDock() {
  const scrim = $('#scrim');
  const dockBtns = document.querySelectorAll('.dock-btn[data-panel]');
  function closeAll() {
    document.querySelectorAll('.panel').forEach((p) => { p.classList.remove('open'); p.setAttribute('aria-hidden', 'true'); });
    dockBtns.forEach((b) => b.setAttribute('aria-expanded', 'false'));
    scrim.classList.remove('show');
  }
  dockBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      const name = btn.dataset.panel;
      const panel = $('#panel-' + name);
      const isOpen = panel.classList.contains('open');
      closeAll();
      if (!isOpen) {
        panel.classList.add('open'); panel.setAttribute('aria-hidden', 'false');
        btn.setAttribute('aria-expanded', 'true');
        scrim.classList.add('show');
      }
    });
  });
  document.querySelectorAll('.panel-close').forEach((b) => b.addEventListener('click', closeAll));
  scrim.addEventListener('click', closeAll);
  $('#topBtn').addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
}

/* ---------- Boot ---------- */
loadContent();
startClock();
Timer.init();
Music.init();
initDock();
