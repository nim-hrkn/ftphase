"""Assemble the trilingual page: marked.html (Japanese, data-i18n ids) + en/*.json + id/*.json -> out html with a JA/EN/ID switch.
Validation: a translation is used only if it parses, has the same multiset of HTML tags as the source and is non-empty;
otherwise the Japanese original stays and the id is listed in build_report.txt."""
import glob, json, os, re, sys, html
D=os.path.dirname(os.path.abspath(__file__)); OUT=sys.argv[1]
t=open(os.path.join(D,"marked.html"),encoding="utf-8").read()
src=json.load(open(os.path.join(D,"src_all.json"),encoding="utf-8"))
tagseq=lambda s: sorted(re.findall(r'<\s*/?\s*([a-zA-Z][a-zA-Z0-9]*)', s))   # real tags only ("< 0.1" is text)
def load(lang):
    d={}; bad=[]
    for f in sorted(glob.glob(os.path.join(D,lang,"src_*.json"))):
        try: chunk=json.load(open(f,encoding="utf-8"))
        except Exception as e: bad.append((f,"json: %s"%e)); continue
        for k,v in chunk.items():
            if k not in src: bad.append((k,"unknown key")); continue
            if not isinstance(v,str) or not v.strip(): bad.append((k,"empty")); continue
            if tagseq(v)!=tagseq(src[k]): bad.append((k,"tag mismatch")); continue
            vv=re.sub(r'title="[^"]*"', '', v).replace(chr(0x30fb), '').replace(chr(0x30fc), '')  # ignore attribute text, bullet and long-vowel marks
            if re.search(r'[\u3040-\u30ff]', vv): bad.append((k,"kana left")); continue
            d[k]=v
    return d,bad
en,bad_en=load("en"); idn,bad_id=load("id")
rep=[f"source blocks {len(src)}", f"en ok {len(en)} bad {len(bad_en)}", f"id ok {len(idn)} bad {len(bad_id)}"]
rep+=["-- en bad: "+", ".join(f"{k}({w})" for k,w in bad_en[:60]), "-- id bad: "+", ".join(f"{k}({w})" for k,w in bad_id[:60])]
open(os.path.join(D,"build_report.txt"),"w").write("\n".join(rep)+"\n"); print("\n".join(rep[:3]))
ui='''
<div id="langsw" style="position:fixed;top:10px;right:12px;z-index:9999;display:flex;gap:4px;font:600 12px/1 system-ui,sans-serif">
<button type="button" data-lang="ja" aria-pressed="true">日本語</button><button type="button" data-lang="en">English</button><button type="button" data-lang="id">Indonesia</button></div>
<style>#langsw button{padding:6px 10px;border:1px solid var(--line,#999);border-radius:6px;background:var(--bg,#fff);color:var(--fg,#222);cursor:pointer}#langsw button[aria-pressed="true"]{background:var(--accent,#2f6fdd);color:#fff;border-color:var(--accent,#2f6fdd)}</style>
<script type="application/json" id="i18n-en">%s</script>
<script type="application/json" id="i18n-id">%s</script>
<script>
(function(){
  var dict={ja:{},en:JSON.parse(document.getElementById('i18n-en').textContent),id:JSON.parse(document.getElementById('i18n-id').textContent)};
  var nodes=document.querySelectorAll('[data-i18n]');
  var svgw={};
  nodes.forEach(function(n){var k=n.getAttribute('data-i18n'); dict.ja[k]=n.innerHTML;
    if(n.namespaceURI==='http://www.w3.org/2000/svg' && n.getComputedTextLength){try{svgw[k]=n.getComputedTextLength();}catch(e){}}});
  function fitSvg(n,k,lang){  /* keep translated SVG labels inside their boxes: shrink the font a little, then squeeze glyph spacing */
    n.removeAttribute('textLength'); n.removeAttribute('lengthAdjust'); n.style.fontSize='';
    if(lang==='ja'||!svgw[k]) return;
    var w0=svgw[k]*1.04, w=n.getComputedTextLength(); if(w<=w0) return;
    var fs=parseFloat(getComputedStyle(n).fontSize)||11; var s=Math.max(0.8,w0/w); n.style.fontSize=(fs*s)+'px';
    w=n.getComputedTextLength(); if(w>w0){n.setAttribute('textLength',w0.toFixed(1)); n.setAttribute('lengthAdjust','spacingAndGlyphs');}
  }
  var titles={ja:document.title,en:'ftphase development status',id:'Status pengembangan ftphase'};
  function apply(lang){
    nodes.forEach(function(n){var k=n.getAttribute('data-i18n');var v=dict[lang][k]; n.innerHTML=(v!==undefined)?v:dict.ja[k]; if(k in svgw) fitSvg(n,k,lang);});
    document.documentElement.lang=(lang==='ja')?'ja':(lang==='en'?'en':'id'); document.title=titles[lang]||titles.ja;
    document.querySelectorAll('#langsw button').forEach(function(b){b.setAttribute('aria-pressed',b.getAttribute('data-lang')===lang?'true':'false');});
    try{localStorage.setItem('ftphase-lang',lang);}catch(e){}
  }
  document.querySelectorAll('#langsw button').forEach(function(b){b.addEventListener('click',function(){apply(b.getAttribute('data-lang'));});});
  var saved=null; try{saved=localStorage.getItem('ftphase-lang');}catch(e){}
  if(saved&&saved!=='ja'&&dict[saved]) apply(saved);
})();
</script>
'''
def jsdump(d): return json.dumps(d, ensure_ascii=False).replace("</", "<\\/")
out=t.replace("</body>", ui % (jsdump(en), jsdump(idn)) + "\n</body>")
assert out!=t
open(OUT,"w",encoding="utf-8").write(out); print("wrote", OUT, len(out))
