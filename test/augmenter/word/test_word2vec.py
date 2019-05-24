import unittest
import os
from dotenv import load_dotenv

import nlpaug.augmenter.word as naw
from nlpaug.util import Action


class TestWord2vec(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        env_config_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '.env'))
        load_dotenv(env_config_path)

    def test_insert(self):
        texts = [
            'The quick brown fox jumps over the lazy dog'
        ]

        aug = naw.Word2vecAug(
            model_path=os.environ.get("MODEL_DIR")+'GoogleNews-vectors-negative300.bin',
            action=Action.INSERT)

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

        aug = naw.Word2vecAug(
            model_path=os.environ.get("MODEL_DIR")+'GoogleNews-vectors-negative300.bin',
            action=Action.SUBSTITUTE)

        for text in texts:
            self.assertLess(0, len(text))
            augmented_text = aug.augment(text)

            self.assertNotEqual(text, augmented_text)

        self.assertLess(0, len(texts))
