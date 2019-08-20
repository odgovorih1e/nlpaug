import unittest

import nlpaug.augmenter.word as naw


class TestStopWords(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stopwords = ['a', 'an', 'the']

    def test_delete(self):
        text = 'The quick brown fox jumps over lazy dog'
        self.assertLess(0, len(text))

        aug = naw.StopWordsAug(stopwords=['fox'])
        augmented_text = aug.augment(text)

        self.assertNotEqual(text, augmented_text)
        self.assertTrue('fox' not in augmented_text)

        # Test case sensitive = False
        aug = naw.StopWordsAug(stopwords=['the'], case_sensitive=False)
        augmented_text = aug.augment(text)

        self.assertNotEqual(text, augmented_text)

        # Test case sensitive = True
        aug = naw.StopWordsAug(stopwords=['the'], case_sensitive=True)
        augmented_text = aug.augment(text)

        self.assertEqual(text, augmented_text)
