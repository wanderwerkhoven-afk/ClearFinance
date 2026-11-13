from types import SimpleNamespace as Obj
from app.parsing import to_blocks,parse_file

class Stub:
    def iterate_items(self):
        bbox=Obj(l=1,t=2,r=40,b=20,coord_origin="BOTTOMLEFT")
        pv=[Obj(page_no=2,bbox=bbox)]
        yield Obj(label="section_header",text="2. Financiële prestaties",prov=pv),0
        yield Obj(label="text",text="De omzet groeide naar 100 miljoen euro.",prov=pv),1
        yield Obj(label="table",text="",prov=pv,export_to_markdown=lambda doc: "|Jaar|Omzet| 2025|100|"),1

def test_docling_mapping_preserves_structure_and_page():
    blocks=to_blocks(Stub())
    assert len(blocks)==3
    assert all(b["page"]==2 and b["section"]=="2. Financiële prestaties" for b in blocks)
    assert blocks[-1]["kind"]=="table"
    assert blocks[1]["bbox"]["origin"].endswith("BOTTOMLEFT")
    assert len({b["id"] for b in blocks})==len(blocks)

def test_invalid_extension_fails_before_import():
    try:
        parse_file(b"content","report.exe")
    except ValueError as exc:
        assert "PDF and DOCX" in str(exc)
    else:
        assert False
