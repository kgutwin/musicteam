import re
from unittest.mock import Mock

import pytest
from chalicelib import pdf
from syrupy.extensions.single_file import SingleFileSnapshotExtension


STATIC_ID = b"/ID[<C29E67C3AFC39BC289C28116217BC2AA><D4C7CDFF2AE8F6901B146F8FCBA86701>]"


def to_test_bytes(doc, compress=False):
    opts = {}
    if compress:
        opts["garbage"] = 3
        opts["deflate"] = True
        opts["use_objstms"] = 1
    return re.sub(rb"/ID\[<[0-9A-F]+><[0-9A-F]+>\]", STATIC_ID, doc.tobytes(**opts))


class PDFSnapshotExtension(SingleFileSnapshotExtension):
    file_extension = "pdf"


@pytest.fixture
def pdf_snapshot(snapshot):
    return snapshot.use_extension(PDFSnapshotExtension)


def test_text_to_pdf_1(pdf_snapshot):
    doc = pdf.text_to_pdf("Hello world")
    assert to_test_bytes(doc) == pdf_snapshot


def test_text_to_pdf_2(pdf_snapshot):
    doc = pdf.text_to_pdf(
        """
Test Song
=========

Verse 1
-------
Bb    Ab
Hello World
"""
    )
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

    doc = pdf.text_to_pdf(
        f"""{title}
{header}

Test one two three
    """
    )
    doc = pdf.add_verse_order(doc, ["V1", "C1", "V2"])
    assert to_test_bytes(doc) == pdf_snapshot
