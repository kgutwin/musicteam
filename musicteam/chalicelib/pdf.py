import pymupdf
from chalicelib.config import OBJECT_BUCKET_NAME
from chalicelib.storage import s3
from chalicelib.types import _PositionSheetDetails
from chalicelib.types import Setlist
from chalicelib.types import SetlistPosition


def read(object_id: str) -> pymupdf.Document:
    resp = s3.get_object(Bucket=OBJECT_BUCKET_NAME, Key=object_id)
    return pymupdf.Document(stream=resp["Body"])


def concatenate(documents: list[pymupdf.Document]) -> pymupdf.Document:
    rv = pymupdf.open()
    for doc in documents:
        rv.insert_pdf(doc)

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
                upper_chars = sum(1 for c in line if c == c.upper())
                space_chars = sum(1 for c in line if c == " ")
                chord_ratio = (upper_chars + space_chars) / len(line)
                fontname = "Courier-Bold" if chord_ratio > 0.8 else "Courier"
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
    while not px.is_unicolor and (rect.y1 + top) > page.rect.height:  # type: ignore[attr-defined]
        rect = pymupdf.IRect(rect.x0, rect.y0 + 2, rect.x1, rect.y1 + 2)
        px = page.get_pixmap(clip=rect)

    if (rect.y1 + top) >= page.rect.height:
        # shift back to the original position
        rect = pymupdf.IRect(left, top, left + width, top + height)

    insert_pt = pymupdf.Point(rect.x0 + margin, rect.y0 + margin)
    for line in verse_order:
        page.insert_text(insert_pt, line, fontname="Helvetica-Bold", fontsize=fontsize)
        insert_pt = pymupdf.Point(insert_pt.x, insert_pt.y + line_height)

    return doc


def make_cover_sheet(
    setlist: Setlist,
    positions: list[SetlistPosition],
    details: list[_PositionSheetDetails],
) -> pymupdf.Document:
    fontsize = 18
    line_height = 20
    insert_pt = pymupdf.Point(72, 72)

    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)  # 8.5 x 11

    page.insert_text(
        insert_pt,
        f"Set list for {setlist.service_date}",
        fontname="Helvetica-Bold",
        fontsize=fontsize,
    )
    insert_pt = pymupdf.Point(insert_pt.x, insert_pt.y + line_height)
    page.insert_text(
        insert_pt,
        f"Leader: {setlist.leader_name}",
        fontname="Helvetica",
        fontsize=fontsize,
    )

    insert_pt = pymupdf.Point(72, 72 * 3)
    for pos in positions:
        row_text = f"- {pos.label}"
        if pos.presenter:
            row_text += f" ({pos.presenter})"
        fontname = "Helvetica-Bold" if pos.is_music else "Helvetica"
        page.insert_text(insert_pt, row_text, fontname=fontname, fontsize=fontsize)
        insert_pt = pymupdf.Point(insert_pt.x, insert_pt.y + line_height)

        sheets = [d for d in details if d.position_id == pos.id]
        if sheets:
            sheet = sheets[0]
            page.insert_text(
                insert_pt,
                f"... {sheet.title} ({sheet.key})",
                fontname=fontname,
                fontsize=fontsize,
            )
            insert_pt = pymupdf.Point(insert_pt.x, insert_pt.y + line_height)

    return doc
