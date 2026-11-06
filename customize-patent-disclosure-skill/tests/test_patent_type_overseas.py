# -*- coding: utf-8 -*-
"""海外公开号类型推断：infer_jurisdiction / infer_overseas_patent_type。

覆盖：US 授权号 → 发明；USD 美国外观 → 外观；JP/KR 实用新型（U/Y）→ 实用新型；
CN 号走原路径（海外推断返回 None）；无法识别返回 None。
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

SHARED_PKG = Path(__file__).resolve().parents[1]
SHARED = SHARED_PKG / "tools"
sys.path.insert(0, str(SHARED))

import patent_type


class InferJurisdictionTests(unittest.TestCase):
    def test_us_grant(self):
        self.assertEqual(patent_type.infer_jurisdiction("US11450918B2"), "US")

    def test_ep_with_kind(self):
        self.assertEqual(patent_type.infer_jurisdiction("EP3389130B1"), "EP")

    def test_jp(self):
        self.assertEqual(patent_type.infer_jurisdiction("JP7371268B2"), "JP")

    def test_cn_via_tail(self):
        self.assertEqual(patent_type.infer_jurisdiction("CN119781913A"), "CN")

    def test_unrecognized(self):
        self.assertIsNone(patent_type.infer_jurisdiction(None))
        self.assertIsNone(patent_type.infer_jurisdiction("12345"))


class InferOverseasPatentTypeTests(unittest.TestCase):
    def test_us_invention(self):
        self.assertEqual(
            patent_type.infer_overseas_patent_type("US11450918B2"),
            patent_type.TYPE_INVENTION,
        )

    def test_us_design(self):
        self.assertEqual(
            patent_type.infer_overseas_patent_type("USD912345S"),
            patent_type.TYPE_DESIGN,
        )

    def test_jp_utility_model(self):
        self.assertEqual(
            patent_type.infer_overseas_patent_type("JP3123456U"),
            patent_type.TYPE_UTILITY_MODEL,
        )

    def test_cn_not_overseas(self):
        # CN 号不属于海外推断范围，须返回 None（走 infer_patent_type_from_pub 原路径）
        self.assertIsNone(patent_type.infer_overseas_patent_type("CN209861402U"))

    def test_garbage(self):
        self.assertIsNone(patent_type.infer_overseas_patent_type(None))
        self.assertIsNone(patent_type.infer_overseas_patent_type("not-a-pub"))


class ResolveReaderPatentTypeOverseasTests(unittest.TestCase):
    def test_overseas_block_after_cn(self):
        out = patent_type.resolve_reader_patent_type(pub="US11450918B2")
        self.assertEqual(out["patent_type"], patent_type.TYPE_INVENTION)
        self.assertEqual(out["source"], "pub_kind_code_overseas")
        self.assertEqual(out["jurisdiction"], "US")
        # 海外种类码推断弱于 CN 种类码：confidence 为 medium
        self.assertEqual(out["confidence"], "medium")

    def test_cn_still_high_confidence(self):
        out = patent_type.resolve_reader_patent_type(pub="CN209861402U")
        self.assertEqual(out["patent_type"], patent_type.TYPE_UTILITY_MODEL)
        self.assertEqual(out["source"], "pub_kind_code")
        self.assertEqual(out["confidence"], "high")
        self.assertEqual(out["jurisdiction"], "CN")


if __name__ == "__main__":
    unittest.main(verbosity=2)
