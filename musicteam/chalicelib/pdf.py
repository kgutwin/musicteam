import pymupdf
from chalicelib.config import OBJECT_BUCKET_NAME
from chalicelib.storage import s3
from chalicelib.types import _PositionSheetDetails
from chalicelib.types import Setlist
from chalicelib.types import SetlistPosition


def read(object_id: str) -> pymupdf.Document:
    resp = s3.get_object(Bucket=OBJECT_BUCKET_NAME, Key=object_id)
    return pymupdf.Document(stream=resp["Body"].read())


def concatenate(
    documents: list[pymupdf.Document], two_page_align: bool = False
) -> pymupdf.Document:
    rv = pymupdf.open()
    for doc in documents:
        rv.insert_pdf(doc)
        if two_page_align and doc is not documents[-1] and doc.page_count % 2 == 1:
            # add a blank page to align to a two-page screen
            rv.new_page(width=612, height=792)  # 8.5 x 11

    return rv


def text_to_pdf(content: str) -> pymupdf.Document:
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)  # 8.5 x 11
    insert_pt = pymupdf.Point(50, 72)

    paragraphs: list[list[str]] = [[]]
    for line in content.splitlines():
        line = line.rstrip()
        if (bool(line) ^ any(pa for pa in paragraphs[-1])) and paragraphs[-1]:
            paragraphs.append([])

        paragraphs[-1].append(line)

    fontsize = 14
    line_height = 15
    first_line = True

    for para in paragraphs:
        height = len(para) * line_height
        if (insert_pt.y + height) > (page.rect.height - 72):
            page = doc.new_page(width=612, height=792)  # 8.5 x 11
            insert_pt = pymupdf.Point(50, 72)

        for line in para:
            if line:
                chord_chars = sum(
                    1 for c in line if c == c.upper() or c in " 0123456789/#b"
                )
                chord_ratio = chord_chars / len(line)
                fontname = "Courier-Bold" if chord_ratio > 0.75 else "Courier"
                if first_line:
                    fontname = "Courier-Bold"
                    first_line = False
                page.insert_text(insert_pt, line, fontname=fontname, fontsize=fontsize)
            insert_pt = pymupdf.Point(insert_pt.x, insert_pt.y + line_height)

    return doc


def add_verse_order(doc: pymupdf.Document, verse_order: list[str]) -> pymupdf.Document:
    fontsize = 18
    line_height = 20
    # rectangle will be 1 inch wide by as high as it needs to be
    margin = 18
    width = 72
    height = ((len(verse_order)) * line_height) + (margin * 2)
    top = 72
    right = 50

    page = doc[0]
    left = page.rect.width - right - width
    rect = pymupdf.IRect(left, top, left + width, top + height)
    px = page.get_pixmap(clip=rect)

    # slide down to try to find a blank spot
    while not px.is_unicolor and (rect.y1 + top) < page.rect.height:  # type: ignore[attr-defined]
        rect = pymupdf.IRect(rect.x0, rect.y0 + 2, rect.x1, rect.y1 + 2)
        px = page.get_pixmap(clip=rect)

    if (rect.y1 + top) >= page.rect.height:
        # shift back to the original position
        rect = pymupdf.IRect(left, top, left + width, top + height)

    # note: the insert_pt is the bottom left corner of the text
    insert_pt = pymupdf.Point(rect.x0 + margin, rect.y0 + margin + fontsize)
    for line in verse_order:
        page.insert_text(insert_pt, line, fontname="Helvetica-Bold", fontsize=fontsize)
        insert_pt = pymupdf.Point(insert_pt.x, insert_pt.y + line_height)

    return doc


def make_cover_sheet(
    setlist: Setlist,
    positions: list[SetlistPosition],
    details: list[_PositionSheetDetails],
) -> pymupdf.Document:
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)  # 8.5 x 11

    css = """
    body {
      margin: 1in;

      font-family: sans-serif;
      font-size: 18pt;
      font-weight: 400;
    }

    h1, h2 {
      font-size: 18pt;
      margin: 0;
    }
    h2 {
      font-weight: 400;
    }
    .set-list {
      padding-left: 0px;
      margin-top: 2em;
      list-style-type: none;
    }
    .set-list li {
      margin-bottom: 0.5em;
    }
    .sheet-list {
      padding-left: 36pt;
      margin-top: 0px;
      margin-bottom: 0px;
      list-style-type: "-";
      font-weight: 900;
    }
    """

    text = pymupdf.Story(user_css=css)  # type: ignore[attr-defined]
    with text.body.add_header(1) as h:
        h.add_text(f"Set list for {setlist.service_date}")
    if setlist.title:
        with text.body.add_header(1) as h:
            h.add_text(f'"{setlist.title}"')

    with text.body.add_header(2) as h:
        h.add_text(f"Leader: {setlist.leader_name}")
    if setlist.participants:
        with text.body.add_header(2) as h:
            h.add_text(f"Team: {', '.join(setlist.participants)}")

    with text.body.add_bullet_list() as b:
        b.add_class("set-list")
        for pos in positions:
            row_text = f"‣ {pos.label}"
            if pos.presenter:
                row_text += f" ({pos.presenter})"

            with b.add_list_item() as row:
                row.add_text(row_text)

                sheets = [d for d in details if d.position_id == pos.id]
                if not sheets:
                    continue

                with row.add_bullet_list() as bb:
                    bb.add_class("sheet-list")
                    titles = set()
                    for sheet in sheets:
                        if sheet.title in titles:
                            continue
                        with bb.add_list_item() as bbrow:
                            bbrow.add_text(f"{sheet.title} ({sheet.key})")
                        titles.add(sheet.title)

    page.insert_htmlbox(page.rect, text)  # type: ignore[attr-defined]
    return doc
