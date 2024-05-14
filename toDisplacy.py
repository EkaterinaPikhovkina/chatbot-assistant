from spacy import displacy


def fDisplacy(doc, style, htmlName):
  fName = htmlName + '.html'
  html = displacy.render(doc, style=style, page=True, options={'collapse_phrases': False})
  from pathlib import Path
  output_path = Path(fName)
  output_path.open("w", encoding="utf-8").write(html)
  import os
  os.startfile(fName)
