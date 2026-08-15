"""export_deck.py 의 PPTX 조립 계약을 검증한다 (stdlib only).

Chrome 을 띄우는 부분은 이 테스트의 대상이 아니다 — 캡처는 환경에 의존하고
느리다. 대신 순수 함수인 슬라이드 분해와 OOXML 조립을 검증한다.
"""
import re
import sys
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import export_deck  # noqa: E402


PNG_1PX = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000a49444154789c6360000002000100" "05fe02fe" "dccc59e7"
    "0000000049454e44ae426082"
)


def storyboard(slide_count):
    slides = "".join(
        f'<div class="ppt-slide"><div class="ppt-top-bar">'
        f'<div class="ppt-top-no">NO. {i:02d}</div></div>'
        f'<div class="ppt-content"><div class="ppt-body-full">본문 {i}</div></div>'
        f'</div>'
        for i in range(1, slide_count + 1)
    )
    return (f'<html><head><style>.x{{}}</style></head><body>'
            f'<div class="docwrap">{slides}</div></body></html>')


class TestSlideSplit(unittest.TestCase):
    def test_splits_every_slide_in_document_order(self):
        slides = export_deck.split_slides(storyboard(4))
        self.assertEqual([no for no, _ in slides], ["01", "02", "03", "04"])

    def test_keeps_nested_divs_intact(self):
        _, block = export_deck.split_slides(storyboard(1))[0]
        self.assertIn("ppt-body-full", block)
        self.assertTrue(block.endswith("</div>"))
        # 여는 div 와 닫는 div 수가 같아야 블록이 온전하다
        self.assertEqual(len(re.findall(r"<div\b", block)),
                         len(re.findall(r"</div>", block)))

    def test_isolated_page_preserves_original_page_number(self):
        """Page No. 는 CSS counter 라 떼어내면 1부터 다시 센다."""
        page = export_deck.isolated_page("<html><head></head>", "<div/>", 14)
        self.assertIn("counter-reset:slide 14", page)


class TestPptxPackage(unittest.TestCase):
    def _build(self, count):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        shots = []
        for i in range(1, count + 1):
            shot = root / f"image{i}.png"
            shot.write_bytes(PNG_1PX)
            shots.append(shot)
        dest = root / "deck.pptx"
        export_deck.build_pptx(shots, dest)
        return zipfile.ZipFile(dest)

    def test_relationship_types_use_the_officedocument_namespace(self):
        """관계 타입 URL 은 패키지 네임스페이스에서 파생시킬 수 없다.

        둘을 문자열 조작으로 합치면 package/2006/officeDocument/2006/... 같은
        무효 URL 이 나오는데 XML 은 여전히 well-formed 라 파싱 검사로는 잡히지
        않는다. 실제로 그 버그가 있었고, 파일은 열리지 않는다.
        """
        pkg = self._build(2)
        for name in pkg.namelist():
            if not name.endswith(".rels"):
                continue
            for url in re.findall(r'Type="([^"]+)"', pkg.read(name).decode()):
                with self.subTest(part=name, url=url):
                    self.assertTrue(
                        url.startswith(
                            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/"),
                        f"관계 타입 URL 이 잘못됐다: {url}")

    def test_every_part_is_wellformed_xml(self):
        pkg = self._build(3)
        for name in pkg.namelist():
            if name.endswith((".xml", ".rels")):
                with self.subTest(part=name):
                    ET.fromstring(pkg.read(name))

    def test_content_types_declares_every_slide(self):
        pkg = self._build(5)
        declared = pkg.read("[Content_Types].xml").decode()
        for i in range(1, 6):
            with self.subTest(slide=i):
                self.assertIn(f'PartName="/ppt/slides/slide{i}.xml"', declared)

    def test_each_slide_references_an_image_that_exists(self):
        pkg = self._build(4)
        names = set(pkg.namelist())
        for i in range(1, 5):
            rels = pkg.read(f"ppt/slides/_rels/slide{i}.xml.rels").decode()
            targets = re.findall(r'Target="\.\./media/([^"]+)"', rels)
            with self.subTest(slide=i):
                self.assertEqual(len(targets), 1)
                self.assertIn(f"ppt/media/{targets[0]}", names)

    def test_presentation_lists_every_slide_with_matching_rels(self):
        pkg = self._build(6)
        pres = pkg.read("ppt/presentation.xml").decode()
        rels = pkg.read("ppt/_rels/presentation.xml.rels").decode()
        rids = re.findall(r'<p:sldId id="\d+" r:id="(rId\d+)"/>', pres)
        self.assertEqual(len(rids), 6)
        for rid in rids:
            with self.subTest(rid=rid):
                self.assertRegex(rels, f'Id="{rid}"[^>]*Target="slides/slide\\d+\\.xml"')

    def test_slide_size_is_16_by_9_widescreen(self):
        pres = self._build(1).read("ppt/presentation.xml").decode()
        self.assertIn(f'<p:sldSz cx="{export_deck.EMU_W}" cy="{export_deck.EMU_H}"/>', pres)
        self.assertAlmostEqual(export_deck.EMU_W / export_deck.EMU_H, 16 / 9, places=3)

    def test_image_fills_the_whole_slide(self):
        slide = self._build(1).read("ppt/slides/slide1.xml").decode()
        self.assertIn('<a:off x="0" y="0"/>', slide)
        self.assertIn(f'<a:ext cx="{export_deck.EMU_W}" cy="{export_deck.EMU_H}"/>', slide)


class TestDesignConstants(unittest.TestCase):
    def test_capture_width_matches_the_template_design_width(self):
        """목업 크기와 배지 top 이 이 폭에서 나온 절대 픽셀값이다."""
        template = (SKILL_ROOT / "resources" / "template.html").read_text(encoding="utf-8")
        self.assertIn(f"max-width: {export_deck.DESIGN_W}px", template)

    def test_render_wait_is_long_enough_for_mermaid(self):
        """대기가 없으면 IA·흐름도·시퀀스가 빈 칸으로 나온다."""
        self.assertGreaterEqual(export_deck.RENDER_WAIT_MS, 5000)


if __name__ == "__main__":
    unittest.main()
