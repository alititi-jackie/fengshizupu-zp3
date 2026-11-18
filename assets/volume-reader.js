if('scrollRestoration' in history) history.scrollRestoration = 'manual';
const bookData = JSON.parse(document.getElementById('originalReaderData').textContent);
const TOTAL = bookData.pages.length - 1;
function label(n) { return bookData.pages[n].label; }
let p = readerPage(bookData.start, TOTAL);
const img = document.getElementById('pg');
const sv = document.getElementById('scrollView');
function src(n){ return bookData.base + 'p' + String(n).padStart(4,'0') + '.webp'; }
function infoFor(n){
  document.getElementById('info').innerHTML = '<b>' + label(n) + '</b><span class="full-only">（共' + TOTAL + '页）</span>';
  const pv = document.getElementById('prev'), nx = document.getElementById('next');
  pv.className = n<=1 ? 'off' : ''; nx.className = n>=TOTAL ? 'off' : '';
}
function render(){
  img.src = src(p);
  img.alt = '《' + bookData.title + '》' + label(p);
  infoFor(p);
  window.scrollTo(0,0);
}
let mode = 'scroll';
try{ mode = localStorage.getItem('readerMode') || 'scroll'; }catch(e){}
if(mode !== 'scroll') mode = 'single';
let lo = 0, hi = 0;
const WIN = 7;
function blockHTML(n){
  return '<div class="spage" data-p="' + n + '"><div class="scap"><b>' + label(n) + '</b></div>' +
    '<button class="reader-image" type="button" aria-label="放大' + label(n) + '"><img class="pageimg" loading="lazy" src="' + src(n) + '" alt="《' + bookData.title + '》' + label(n) + '"></button></div>';
}
function blockEl(n){ return sv.querySelector('.spage[data-p="' + n + '"]'); }
function buildScroll(center){
  lo = Math.max(1, center - WIN); hi = Math.min(TOTAL, center + WIN);
  let h = ''; for(let n = lo; n <= hi; n++) h += blockHTML(n);
  sv.innerHTML = h;
}
function barOffset(){
  const nav = document.querySelector('.mainnav');
  const bar = document.querySelector('.readerbar');
  const dl = document.querySelector('.dlrow');
  return (nav ? nav.offsetHeight : 48) + (bar ? bar.offsetHeight : 50) + (dl ? dl.offsetHeight : 0) + 6;
}
let holdUntil = 0;
function scrollToPage(n, smooth){
  const el = blockEl(n); if(!el) return;
  const y = el.getBoundingClientRect().top + window.scrollY - barOffset();
  holdUntil = Date.now() + 180;
  window.scrollTo({ top: y, behavior: smooth ? 'smooth' : 'auto' });
}
function anchorTop(){
  const els = sv.querySelectorAll('.spage');
  for(let i = 0; i < els.length; i++){
    const r = els[i].getBoundingClientRect();
    if(r.bottom > 0) return { n: parseInt(els[i].dataset.p), top: r.top };
  }
  return null;
}
function restoreAnchor(a){
  if(!a) return;
  const el = blockEl(a.n);
  if(el) window.scrollBy(0, el.getBoundingClientRect().top - a.top);
}
function currentFromScroll(){
  const line = barOffset() + 30;
  let cur = lo, best = 0;
  const els = sv.querySelectorAll('.spage');
  for(let i = 0; i < els.length; i++){
    const r = els[i].getBoundingClientRect();
    if(r.top <= line) cur = parseInt(els[i].dataset.p);
    if(r.top <= line && r.bottom > line){ best = parseInt(els[i].dataset.p); break; }
  }
  return best || cur;
}
let ticking = false;
function onScroll(){
  if(mode !== 'scroll' || ticking) return;
  ticking = true;
  requestAnimationFrame(() => {
    ticking = false;
    if(mode !== 'scroll' || Date.now() < holdUntil) return;
    const cur = currentFromScroll();
    if(cur !== p){ p = cur; updateReaderURL(p); infoFor(p); }
    if(hi < TOTAL && hi - p <= 3){
      let h = ''; const nhi = Math.min(TOTAL, hi + WIN);
      for(let n = hi + 1; n <= nhi; n++) h += blockHTML(n);
      sv.insertAdjacentHTML('beforeend', h); hi = nhi;
    }
    if(lo > 1 && p - lo <= 3){
      let h = ''; const nlo = Math.max(1, lo - WIN);
      for(let n = nlo; n <= lo - 1; n++) h += blockHTML(n);
      const a = anchorTop();
      sv.insertAdjacentHTML('afterbegin', h);
      restoreAnchor(a);
      lo = nlo;
    }
    if(hi - p > WIN + 10){
      const n = p + WIN + 4;
      sv.querySelectorAll('.spage').forEach(el => { if(parseInt(el.dataset.p) > n) el.remove(); });
      hi = n;
    }
    if(p - lo > WIN + 10){
      const n = p - WIN - 4;
      const a = anchorTop();
      sv.querySelectorAll('.spage').forEach(el => { if(parseInt(el.dataset.p) < n) el.remove(); });
      restoreAnchor(a);
      lo = n;
    }
  });
}
window.addEventListener('scroll', onScroll, { passive: true });
function gotoPage(n, smooth){
  p = Math.max(1, Math.min(TOTAL, n));
  updateReaderURL(p);
  if(mode === 'scroll'){
    if(p < lo || p > hi) buildScroll(p);
    infoFor(p);
    scrollToPage(p, !!smooth);
  } else render();
}
function setMode(m){
  mode = m;
  try{ localStorage.setItem('readerMode', m); }catch(e){}
  showMode(m);
  const single = m === 'single';
  document.getElementById('singlePage').style.display = single ? '' : 'none';
  sv.style.display = single ? 'none' : '';
  if(single) render();
  else { buildScroll(p); infoFor(p); scrollToPage(p, false);
    requestAnimationFrame(() => { if(mode === 'scroll') scrollToPage(p, false); }); }
}
const imageDialog = bindImageDialog();
document.getElementById('singlePage').onclick = () => imageDialog.open(src(p), label(p));
sv.addEventListener('click', e => {
  const button = e.target.closest('.reader-image');
  if (!button) return;
  const n = Number(button.closest('.spage').dataset.p);
  imageDialog.open(src(n), label(n));
});
const showMode = bindReaderControls({
  previous: document.getElementById('prev'),
  next: document.getElementById('next'),
  move(value, relative) {
    const page = relative ? p + value : value;
    if (page >= 1 && page <= TOTAL) gotoPage(page, false);
  },
  setMode,
  jumpTo: value => Number.isInteger(value) && value >= 1 && value <= TOTAL ? value : undefined,
  dialog: imageDialog.dialog,
});
setMode(mode);
