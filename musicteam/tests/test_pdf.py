from unittest.mock import Mock

from chalicelib import pdf


def to_test_bytes(doc, compress=False):
    opts = {}
    if compress:
        opts["garbage"] = 3
        opts["deflate"] = True
        opts["use_objstms"] = 1
    return doc.tobytes(**opts)


def test_text_to_pdf_1(pdf_snapshot):
    doc = pdf.text_to_pdf("Hello world")
    assert to_test_bytes(doc) == pdf_snapshot


def test_text_to_pdf_2(pdf_snapshot):
    doc = pdf.text_to_pdf("""
Test Song
=========

Verse 1
-------
Bb    Ab
Hello World
""")
    assert to_test_bytes(doc) == pdf_snapshot


def test_make_cover_sheet(pdf_snapshot):
    setlist = Mock(
        service_date="2026-01-05",
        title="Test Setlist",
        leader_name="Pytest",
        participants=["foo", "bar"],
    )
    positions = [
        Mock(id="lp:a", label="First", is_music=True, presenter="Someone"),
        Mock(id="lp:b", label="Next", is_music=False, presenter=None),
        Mock(id="lp:c", label="Last", is_music=True, presenter=None),
    ]
    details = [
        Mock(position_id="lp:a", title="Song One", key="D"),
        Mock(position_id="lp:c", title="Song Two", key="E"),
    ]

    doc = pdf.make_cover_sheet(setlist, positions, details)
    assert to_test_bytes(doc, compress=True) == pdf_snapshot


def test_add_verse_order(pdf_snapshot):
    # make a document with a very long title
    title = "Hello " * 10
    header = "=" * 59

    doc = pdf.text_to_pdf(f"""{title}
{header}

Test one two three
    """)
    doc = pdf.add_verse_order(doc, ["V1", "C1", "V2"])
    assert to_test_bytes(doc) == pdf_snapshot
