import json
from pathlib import Path
import tempfile
import unittest

from evaluate import ROOT, load_artifacts, metrics, read_questions, validate_labels


class EvaluationTests(unittest.TestCase):
    def test_rejects_stale_embeddings(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            (target / 'manifest.json').write_text(json.dumps({'input_sha256': 'stale'}))
            (target / 'chunks.jsonl').write_bytes(b'old corpus')
            corpus = target / 'current.jsonl'
            corpus.write_bytes(b'new corpus')
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                load_artifacts(target, corpus)

    def test_metrics_include_misses_in_denominator(self):
        result = metrics([{'first_relevant_rank': n} for n in [1, 3, 10, None]])
        self.assertEqual(result['hit_at_1'], .25)
        self.assertEqual(result['hit_at_5'], .5)
        self.assertEqual(result['hit_at_10'], .75)
        self.assertAlmostEqual(result['mrr_at_10'], (1 + 1/3 + 1/10) / 4)
        self.assertIsNone(metrics([])['mrr_at_10'])

    def test_question_split_and_unicode(self):
        questions = read_questions(ROOT / 'eval/questions_draft.md')
        self.assertEqual(len(questions), 20)
        self.assertEqual(sum(q['answerable'] for q in questions), 16)
        self.assertEqual({q['language'] for q in questions}, {'English', 'Urdu', 'Roman Urdu'})
        self.assertIn('انفرادی', questions[1]['question'])

    def test_label_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'labels.json'
            questions = [dict(question_id='Q01', answerable=True), dict(question_id='Q17', answerable=False)]
            chunks = [dict(chunk_id='c1')]
            self.assertEqual(validate_labels(path, questions, chunks, 'c', 'q'), {})
            data = dict(corpus_sha256='c', questions_sha256='q',
                        labels={'Q01': dict(reviewed=True, relevant_chunk_ids=['c1'])})
            path.write_text(json.dumps(data))
            self.assertEqual(validate_labels(path, questions, chunks, 'c', 'q'), {'Q01': {'c1'}})
            with self.assertRaisesRegex(ValueError, 'different corpus'):
                validate_labels(path, questions, chunks, 'changed', 'q')
            data['labels']['Q01']['relevant_chunk_ids'] = ['unknown']
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'chunk IDs'):
                validate_labels(path, questions, chunks, 'c', 'q')
            data['labels'] = {'Q17': dict(reviewed=True, relevant_chunk_ids=['c1'])}
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'answerable'):
                validate_labels(path, questions, chunks, 'c', 'q')


if __name__ == '__main__':
    unittest.main()
