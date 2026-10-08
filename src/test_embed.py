import unittest

import numpy as np

from embed import encode_texts


class FakeModel:
    max_seq_length = 30

    def tokenizer(self, inputs, truncation):
        assert truncation is False
        return {"input_ids": [list(range(len(text))) for text in inputs]}

    def encode(self, inputs, **kwargs):
        self.inputs = inputs
        assert kwargs['normalize_embeddings']
        return np.tile([1.0, 0.0], (len(inputs), 1))


class EmbedTests(unittest.TestCase):
    def test_prefixes_and_shape(self):
        model = FakeModel()
        vectors, lengths = encode_texts(model, ['hello', 'سلام'], 'passage')
        self.assertEqual(model.inputs, ['passage: hello', 'passage: سلام'])
        self.assertEqual(vectors.shape, (2, 2))
        self.assertEqual(vectors.dtype, np.float32)
        encode_texts(model, ['salam'], 'query')
        self.assertEqual(model.inputs, ['query: salam'])

    def test_rejects_truncation_before_encoding(self):
        model = FakeModel()
        with self.assertRaisesRegex(ValueError, 'exceed'):
            encode_texts(model, ['x' * 50], 'passage')
        self.assertFalse(hasattr(model, 'inputs'))

    def test_invalid_kind(self):
        with self.assertRaises(ValueError):
            encode_texts(FakeModel(), ['hello'], 'invalid')


if __name__ == '__main__':
    unittest.main()
