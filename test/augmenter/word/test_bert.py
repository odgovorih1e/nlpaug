import unittest
import os
from dotenv import load_dotenv

import nlpaug.augmenter.word as naw
from nlpaug.util import Action


class TestBert(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        env_config_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '.env'))
        load_dotenv(env_config_path)

    def test_insert(self):
        texts = [
            'The quick brown fox jumps over the lazy dog'
        ]

        aug = naw.BertAug(action=Action.INSERT)

        for text in texts:
            self.assertLess(0, len(text))
            augmented_text = aug.augment(text)

            self.assertLess(len(text.split(' ')), len(augmented_text.split(' ')))
            self.assertNotEqual(text, augmented_text)

        self.assertLess(0, len(texts))

    def test_substitute(self):
        texts = [
            'The quick brown fox jumps over the lazy dog'
        ]

        aug = naw.BertAug(action=Action.SUBSTITUTE)

        for text in texts:
            self.assertLess(0, len(text))
            augmented_text = aug.augment(text)

            self.assertNotEqual(text, augmented_text)

        self.assertLess(0, len(texts))

    def test_substitute_stopwords(self):
        texts = [
            'The quick brown fox jumps over the lazy dog'
        ]

        stopwords = [t.lower() for t in texts[0].split(' ')[:3]]
        aug_n = 3

        aug = naw.BertAug(action=Action.SUBSTITUTE, aug_n=3, stopwords=stopwords)

        for text in texts:
            self.assertLess(0, len(text))
            augmented_text = aug.augment(text)

            augmented_tokens = aug.tokenizer(augmented_text)
            tokens = aug.tokenizer(text)

            augmented_cnt = 0

            for token, augmented_token in zip(tokens, augmented_tokens):
                if token.lower() in stopwords and len(token) > aug_n:
                    self.assertEqual(token.lower(), augmented_token)
                else:
                    augmented_cnt += 1

            self.assertGreater(augmented_cnt, 0)

        self.assertLess(0, len(texts))
