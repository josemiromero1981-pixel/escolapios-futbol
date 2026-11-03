"""Genera index.html (web pública) a partir de app.html (contenido de la app, el mismo que se publica en el artefacto de Claude)."""
import pathlib
d=pathlib.Path(__file__).parent
body=(d/"app.html").read_text(encoding="utf-8")
(d/"index.html").write_text((d/"head.html").read_text(encoding="utf-8")+body+"\n</body>\n</html>\n",encoding="utf-8")
print("index.html generado")
