"""Genera matchday/index.html (Escolapios Matchday para el iPhone) a partir de matchday/source.html
(el HTML del artefacto de Claude) y app.html.
La página publicada lee los datos de ../app.html cada vez que se abre, así que se actualiza sola con la
tarea diaria; los datos incrustados solo se usan si no hay conexión."""
import pathlib, re
d = pathlib.Path(__file__).parent
src = (d / "matchday" / "source.html").read_text(encoding="utf-8")
app = (d / "app.html").read_text(encoding="utf-8")

def block(s):
    a = re.search(r'^const C=\{', s, re.M)
    b = re.search(r'^const CHANGES=\[.*?\];[ \t]*$', s[a.start():], re.M | re.S)
    return a.start(), a.start() + b.end()

# Datos de respaldo = los de app.html de ahora
a0, a1 = block(app); m0, m1 = block(src)
src = src[:m0] + app[a0:a1] + src[m1:]

# Cabecera propia (fuera de claude.ai) con lo necesario para "Añadir a pantalla de inicio"
body = src[src.index("<body>") + len("<body>"):]
body = body.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
body = re.sub(r'<title>.*?</title>\n?', "", body, count=1)
body = body[:body.rindex("</body>")]
head = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<title>Escolapios Matchday</title>
<meta name="theme-color" content="#06110d">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Matchday">
<link rel="apple-touch-icon" href="../apple-touch-icon.png">
<link rel="icon" type="image/png" href="../icon-192.png">
<link rel="manifest" href="manifest.webmanifest">
<style>:root{color-scheme:dark;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}html{background:#06110d;scroll-padding-top:env(safe-area-inset-top,0px)}body{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif}img{max-width:100%}[hidden]:not([hidden=until-found i]){display:none!important}</style>
</head>
<body>
"""
# Los scripts quedan inertes y un cargador los ejecuta con los datos frescos de ../app.html
n = body.count("<script>")
assert n == 2, n
body = body.replace("<script>", '<script type="text/plain" data-md>')
loader = r"""<script>
(function(){
  var parts=[].slice.call(document.querySelectorAll('script[data-md]')),done=false;
  function cut(t){var a=t.search(/^const C=\{/m);if(a<0)return null;var r=/^const CHANGES=\[[\s\S]*?\];[ \t]*$/m.exec(t.slice(a));return r?[a,a+r.index+r[0].length]:null}
  function run(fresh){
    if(done)return;done=true;
    parts.forEach(function(p,i){
      var t=p.textContent;
      if(i===0&&fresh){var x=cut(t),y=cut(fresh);if(x&&y)t=t.slice(0,x[0])+fresh.slice(y[0],y[1])+t.slice(x[1])}
      var s=document.createElement('script');s.text=t;p.parentNode.replaceChild(s,p);
    });
  }
  setTimeout(function(){run(null)},5000);
  fetch('../app.html?t='+Date.now(),{cache:'no-store'}).then(function(r){if(!r.ok)throw 0;return r.text()}).then(run,function(){run(null)});
})();
</script>
"""
out = head + body + loader + "</body>\n</html>\n"
(d / "matchday" / "index.html").write_text(out, encoding="utf-8")
print("matchday/index.html generado")
