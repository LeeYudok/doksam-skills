#!/usr/bin/env python3
"""이슈 #13 기하 검증용 프로브 문서 생성기 (stdlib only).

template.html 의 <style> 을 그대로 인라인해, 목업 1/2/3/4개 슬라이드를 만들고
브라우저에서 열면 스스로 치수를 재서 PASS/FAIL 표를 그린다. 재실행:

    python3 scripts/build_multimock_probe.py

산출물: scripts/multimock-probe.html
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
css = re.search(
    r"<style>(.*?)</style>",
    (ROOT / "skills/mobile-web-planner/resources/template.html").read_text(encoding="utf-8"),
    re.DOTALL,
).group(1)


def mock(caption, badges):
    b = "\n".join(
        f'              <span class="pointer-badge" style="position:absolute; '
        f'top:{t}px; left:2px; z-index:10;">{n}</span>'
        for n, t in badges
    )
    cap = f'\n          <div class="mock-caption">{caption}</div>' if caption else ""
    return f"""        <div class="mock">
          <div class="mock-screen">
            <div class="mock-status"></div>
            <div class="mock-header"><span>HEADER</span></div>
            <div class="mock-body" style="position:relative;">
{b}
              <div data-probe-content style="background:#eee; height:60px; margin-bottom:12px;">content A</div>
              <div style="background:#eee; height:60px;">content B</div>
            </div>
            <div class="mock-footer">
              <div class="mock-tab active">Home</div>
              <div class="mock-tab">Search</div>
            </div>
          </div>{cap}
        </div>"""


def slide(no, title, mocks):
    nl = "\n"
    return f"""
  <div class="ppt-slide" data-mockcount="{len(mocks)}">
    <div class="ppt-top-bar">
      <div class="ppt-top-no">NO. {no}</div>
      <div class="ppt-top-title">{title}</div>
      <div class="ppt-top-proj">PROBE</div>
    </div>
    <div class="ppt-meta-bar">
      <div class="ppt-meta-label">Location</div>
      <div class="ppt-meta-value">홈 &gt; 프로브</div>
    </div>
    <div class="ppt-content">
      <div class="ppt-wireframe">
{nl.join(mocks)}
      </div>
      <div class="ppt-desc-panel">
        <div class="ppt-desc-header">Description</div>
        <div class="ppt-desc-body"><ul class="desc-list">
          <li><span class="desc-num">(1)</span> <div>probe item</div></li>
        </ul></div>
      </div>
    </div>
    <div class="ppt-footer">PROBE | Ver.0</div>
  </div>
"""


# 1개 슬라이드는 회귀 기준선 — 캡션 없이 기존 예시와 동일한 구조.
S1 = slide("06.1", "1 mock (regression baseline, no caption)", [mock(None, [(1, 20), (2, 100)])])
S2 = slide("06.2", "2 mocks (zoom 0.9, 2단 번호)", [mock("기본 상태", [("1-1", 20), ("1-2", 100)]), mock("선택됨", [("2-1", 20)])])
S3 = slide("06.3", "3 mocks (zoom 0.9, 2단 번호)", [mock("입력", [("1-1", 20)]), mock("확인", [("2-1", 20)]), mock("완료", [("3-1", 20)])])
S4 = slide("06.4", "4 mocks (zoom 0.68, 2단 번호)", [mock(f"단계 {i}", [(f"{i}-1", 20)]) for i in range(1, 5)])

SCRIPT = r"""
<script>
function r(el){return el.getBoundingClientRect();}
function inner(el){
  var cs=getComputedStyle(el), b=r(el);
  return {left:b.left+parseFloat(cs.borderLeftWidth), right:b.right-parseFloat(cs.borderRightWidth),
          top:b.top+parseFloat(cs.borderTopWidth), bottom:b.bottom-parseFloat(cs.borderBottomWidth)};
}
var rows=[], fails=0;
function chk(name, actual, expected, tol){
  var ok = (typeof expected==='boolean') ? (actual===expected) : Math.abs(actual-expected)<=tol;
  if(!ok) fails++;
  rows.push([name, (typeof actual==='number'?actual.toFixed(2):String(actual)),
             (typeof expected==='number'?expected.toFixed(2):String(expected)), ok?'PASS':'FAIL']);
}
document.querySelectorAll('.ppt-slide').forEach(function(slide){
  var n = +slide.dataset.mockcount, tag='['+n+'-mock] ';
  var wf = slide.querySelector('.ppt-wireframe'), wi = inner(wf);
  chk(tag+'ppt-wireframe content width', wi.right-wi.left, 980, 1.5);
  chk(tag+'ppt-wireframe content height', wi.bottom-wi.top, 643.5, 1.5);
  chk(tag+'ppt-wireframe no h-overflow (scrollWidth<=clientWidth)', wf.scrollWidth<=wf.clientWidth, true);
  chk(tag+'ppt-wireframe no v-overflow (scrollHeight<=clientHeight)', wf.scrollHeight<=wf.clientHeight, true);
  var mocks=[].slice.call(slide.querySelectorAll('.mock'));
  var z = (n>=4) ? 0.68 : 0.9;
  mocks.forEach(function(m,i){
    var mr=r(m);
    chk(tag+'mock['+i+'] visual width', mr.width, 320*z, 1.0);
    chk(tag+'mock['+i+'] visual height', mr.height, 600*z, 1.5);
    chk(tag+'mock['+i+'] inside wireframe (left)', mr.left>=wi.left-0.5, true);
    chk(tag+'mock['+i+'] inside wireframe (right)', mr.right<=wi.right+0.5, true);
    if(i>0) chk(tag+'gap mock['+(i-1)+']->mock['+i+']', mr.left-r(mocks[i-1]).right, 24, 1.0);
    var cap=m.querySelector('.mock-caption');
    if(cap) chk(tag+'caption['+i+'] bottom inside wireframe', r(cap).bottom<=wi.bottom+0.5, true);
    var ms=m.querySelector('.mock-screen'), body=m.querySelector('.mock-body');
    var content=body.querySelector('[data-probe-content]');
    m.querySelectorAll('.pointer-badge').forEach(function(b,j){
      var br=r(b), msr=r(ms), bodyr=r(body), cr=r(content);
      chk(tag+'badge['+i+','+j+'] not clipped by mock-screen (left)', br.left>=msr.left-0.5, true);
      chk(tag+'badge['+i+','+j+'] right of mock-body box left', br.left>=bodyr.left-0.5, true);
      chk(tag+'badge['+i+','+j+'] right edge <= content left (gutter clear)', br.right<=cr.left+0.02, true);
      chk(tag+'badge['+i+','+j+'] gutter clearance >= 0', cr.left-br.right >= -0.02, true);
      // 배지는 가변 폭이다. 한 글자는 24px, 2단 번호는 내용만큼 넓어진다.
      chk(tag+'badge['+i+','+j+'] width >= 24 (min-width)', br.width >= 24*z-0.5, true);
    });
  });
});
var html='<h2 style="font-family:monospace">multi-mock probe: '+(fails?fails+' FAIL':'ALL PASS')+' ('+rows.length+' checks)</h2>'
 +'<p style="font-family:monospace">window.innerWidth='+window.innerWidth+' (must be &gt;= 1480 so the slide is 1400px); slide width='+r(document.querySelector('.ppt-slide')).width.toFixed(2)+'</p>'
 +'<table style="font-family:monospace;font-size:12px;border-collapse:collapse;background:#fff">'
 +'<tr><th style="border:1px solid #ccc;padding:3px 8px">check</th><th style="border:1px solid #ccc;padding:3px 8px">actual</th><th style="border:1px solid #ccc;padding:3px 8px">expected</th><th style="border:1px solid #ccc;padding:3px 8px">result</th></tr>'
 +rows.map(function(x){return '<tr'+(x[3]==='FAIL'?' style="background:#fdd"':'')+'>'+x.map(function(c){return '<td style="border:1px solid #ccc;padding:3px 8px">'+c+'</td>';}).join('')+'</tr>';}).join('')
 +'</table>';
document.getElementById('probe-out').innerHTML=html;
document.title=(fails?fails+' FAIL':'ALL PASS')+' - multi-mock probe';
</script>
"""

DOC = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>multi-mock probe</title>
<style>
{css}
</style>
</head>
<body>
<div id="probe-out" style="max-width:1400px; margin:0 auto 40px; background:#fff; padding:20px;">measuring...</div>
<div class="docwrap">
{S1}{S2}{S3}{S4}</div>
{SCRIPT}
</body>
</html>
"""

out = ROOT / "scripts" / "multimock-probe.html"
out.write_text(DOC, encoding="utf-8")
print(f"wrote {out.relative_to(ROOT)} ({len(DOC)} bytes)")
