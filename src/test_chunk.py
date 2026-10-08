import unittest

from chunk import chunk_pages, split_body


class ChunkTests(unittest.TestCase):
    def test_lossless_splitting_in_both_languages(self):
        for body in ("First sentence. Second sentence!\n" * 30,
                     "یہ ایک جملہ ہے۔ اگلا جملہ ہے؟\n" * 30, "x" * 300):
            parts = list(split_body(body, 80))
            self.assertEqual("".join(p[2] for p in parts), body)
            for start, end, text in parts:
                self.assertEqual(text, body[start:end])
                self.assertLessEqual(len(text), 80)

    def test_metadata_budget_and_section_boundaries(self):
        page = dict(pair_id="1", lang="ur", title="عنوان", url="https://example.com",
                    file="1_ur.html", accessed="2026-10-08", sections=[
                        dict(heading="پہلا", lines=["یہ ایک جملہ ہے۔ " * 50]),
                        dict(heading="دوسرا", lines=["الگ مواد"]),
                    ])
        chunks = chunk_pages([page], 100)
        self.assertEqual(chunks, chunk_pages([page], 100))
        self.assertEqual(len(chunks), len({c['chunk_id'] for c in chunks}))
        self.assertEqual(chunks[-1]['content'], "الگ مواد")
        for chunk in chunks:
            self.assertLessEqual(len(chunk['text']), 100)
            self.assertEqual(chunk['url'], page['url'])
        for index, section in enumerate(page['sections']):
            self.assertEqual(''.join(c['content'] for c in chunks if c['section_index'] == index),
                             '\n'.join(section['lines']).strip())

    def test_invalid_budget(self):
        with self.assertRaises(ValueError):
            chunk_pages([], 0)


if __name__ == "__main__":
    unittest.main()
