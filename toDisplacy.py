# toDisplacy.py


from spacy import displacy


def f_displacy(doc, style, htmlName):
    """
    Generates an HTML file visualizing a spaCy document's entities or dependencies.

    Parameters:
    - doc: The spaCy document to be visualized.
    - style: The visualization style ('ent' for entities, 'dep' for dependencies).
    - htmlName: The base name of the output HTML file.

    The function creates an HTML file with the visualization and opens it using the default web browser.
    """
    f_name = htmlName + '.html'
    html = displacy.render(doc, style=style, page=True, options={'collapse_phrases': False})
    from pathlib import Path
    output_path = Path(f_name)
    output_path.open("w", encoding="utf-8").write(html)
    import os
    os.startfile(f_name)
