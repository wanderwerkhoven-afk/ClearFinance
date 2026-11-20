from pathlib import Path
import pytest
from research_v2.demo import build_demo,render_html
from research_v2.input import load_document,text_blocks

FIXTURE=Path(__file__).parents[1]/"fixtures/synthetic_report.json"

def test_complete_demo_detects_changed_number():
    result=build_demo(str(FIXTURE))
    assert len(result["injected"]["layers"])==3
    assert result["comparison"]["numeric_before"]=="pass"
    assert result["comparison"]["numeric_after"]=="review"
    assert 0<result["comparison"]["rouge1"]<1
    assert "125" in render_html(result)
    assert "p.1:" in render_html(result)

def test_demo_does_not_mutate_original_source():
    result=build_demo(str(FIXTURE))
    assert "120 miljoen" in result["baseline"]["source"][0]["text"]
    assert result["baseline"]["layers"]!=result["injected"]["layers"]

def test_text_ingestion_from_file(tmp_path):
    file=tmp_path/"input.txt"
    file.write_text("Financieel overzicht\n\nDe omzet bedroeg 120 miljoen in 2025.\n\nRisico's\n\nHet renterisico neemt toe.",encoding="utf8")
    blocks=load_document(file)
    assert len(blocks)>=3
    assert all(b.page==1 and b.id for b in blocks)

def test_pdf_ingestion_from_generated_test_pdf(tmp_path):
    fitz=pytest.importorskip("fitz")
    path=tmp_path/"synthetic.pdf"
    doc=fitz.open();page=doc.new_page()
    page.insert_text((70,70),"De omzet bedroeg 120 miljoen in 2025.",fontsize=12)
    doc.save(path);doc.close()
    blocks=load_document(path)
    assert len(blocks)>=1
    assert blocks[0].page==1
    assert "120 miljoen" in blocks[0].text

def test_unsupported_extension(tmp_path):
    with pytest.raises(ValueError):
        load_document(tmp_path/"bad.docx")
