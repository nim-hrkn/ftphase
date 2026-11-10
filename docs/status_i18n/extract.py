"""Mark translatable blocks in the artifact HTML with data-i18n ids and write source chunks for the translators."""
import re, json, os, sys
W=sys.argv[1]; OUT=sys.argv[2]
t=open(W,encoding="utf-8").read()
jp=re.compile(r'[぀-ヿ一-鿿]')
TAGS=r'p|li|h1|h2|h3|h4|td|th|summary|figcaption|caption|title|text|dt|dd|a|button'
pat=re.compile(r'<(%s)(\s[^>]*)?>(.*?)</\1>' % TAGS, re.S)
divpat=re.compile(r'<(div|footer)(\s+class="(?:k|s|eyebrow|sub|hint|small|note|lede|warn|callout)"[^>]*|)>(.*?)</\1>', re.S)
n=0; src={}
def mark(m):
    global n
    tag, attrs, inner = m.group(1), m.group(2) or "", m.group(3)
    if not jp.search(inner) or 'data-i18n=' in attrs:
        return m.group(0)
    if tag=="a" and "<" in inner and jp.search(re.sub(r'<[^>]+>','',inner)) is None:
        return m.group(0)
    n+=1; key=f"{n}"; src[key]=inner
    return f"<{tag}{attrs} data-i18n=\"{key}\">{inner}</{tag}>"
# block elements first (td/th/p/li/h*/text...), then tile divs and links that are not inside already-marked blocks
t2=pat.sub(mark, t)
t2=divpat.sub(mark, t2)
# nested marks: a marked <a>/<td> inside a marked <p>/<li> would be translated twice -> drop inner marks
def drop_inner(m):
    inner=m.group(3); cleaned=re.sub(r' data-i18n="\d+"', '', inner)
    for k in re.findall(r' data-i18n="(\d+)"', inner): src.pop(k, None)
    return f"<{m.group(1)}{m.group(2)}>{cleaned}</{m.group(1)}>"
t2=re.compile(r'<(%s)(\s[^>]*data-i18n="\d+"[^>]*)>(.*?)</\1>' % TAGS, re.S).sub(drop_inner, t2)
# resync src with what remains marked
keys=set(re.findall(r' data-i18n="(\d+)"', t2)); src={k:v for k,v in src.items() if k in keys}
# fix inner html for entries whose inner changed by drop_inner (take from the file)
for m in re.finditer(r'<(%s|div|footer)(\s[^>]*?data-i18n="(\d+)"[^>]*)>(.*?)</\1>' % TAGS, t2, re.S):
    src[m.group(3)]=m.group(4)
open(os.path.join(OUT,"marked.html"),"w",encoding="utf-8").write(t2)
s=re.sub(r'data:image/png;base64,[A-Za-z0-9+/=]+','IMG',t2)
left=re.findall(r'>([^<]*[぀-ヿ一-鿿][^<]*)<', re.sub(r'<(%s|div|footer)(\s[^>]*?data-i18n="\d+"[^>]*)>(.*?)</\1>' % TAGS, '', s, flags=re.S))
print("marked", len(src), "chars", sum(len(re.sub(r'<[^>]+>','',v)) for v in src.values()), "| leftover japanese nodes:", len(left), [x[:40] for x in left[:10]])
# chunks of ~5000 chars (tags stripped)
items=sorted(src.items(), key=lambda kv:int(kv[0])); chunks=[]; cur={}; size=0
for k,v in items:
    L=len(re.sub(r'<[^>]+>','',v)); 
    if size+L>5000 and cur: chunks.append(cur); cur={}; size=0
    cur[k]=v; size+=L
if cur: chunks.append(cur)
for i,c in enumerate(chunks): json.dump(c, open(os.path.join(OUT,f"src_{i:02d}.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=0)
json.dump(src, open(os.path.join(OUT,"src_all.json"),"w",encoding="utf-8"), ensure_ascii=False)
print("chunks", len(chunks), [len(c) for c in chunks])
