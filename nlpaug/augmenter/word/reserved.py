"""
    Augmenter that apply target word replacement operation to textual input.
"""
import re
from collections import defaultdict

from nlpaug.augmenter.word import WordAugmenter
from nlpaug.util import Action, Doc


class ReservedAug(WordAugmenter):
    CONNECT_TOKEN = 'nnnnn'
    """
    Augmenter that apply target word replacement for augmentation.

    :param float aug_p: Percentage of word will be augmented. 
    :param int aug_min: Minimum number of word will be augmented.
    :param int aug_max: Maximum number of word will be augmented. If None is passed, number of augmentation is
        calculated via aup_p. If calculated result from aug_p is smaller than aug_max, will use calculated result from
        aug_p. Otherwise, using aug_max.
    :param list reserved_tokens: A list of swappable tokens (a list of list). For example, "FWD", "Fwd" and "FW" 
        are referring to "foward" in email communcation while "Sincerely" and "Best Regards" treated as same 
        meaning. The input should be [["FWD", "Fwd", "FW"], ["Sincerely", "Best Regards"]]. 
    :param bool case_sensitive: Default is True. If True, it will only replace alternative token if all cases are same.
    :param func tokenizer: Customize tokenization process
    :param func reverse_tokenizer: Customize reverse of tokenization process
    :param str name: Name of this augmenter

    >>> import nlpaug.augmenter.word as naw
    >>> aug = naw.ReservedAug()
    """

    def __init__(self, reserved_tokens, action=Action.SUBSTITUTE, case_sensitive=True, name='Reserved_Aug', 
        aug_min=1, aug_max=10, aug_p=0.3, tokenizer=None, reverse_tokenizer=None, 
        verbose=0):
        super().__init__(
            action=action, name=name, aug_p=aug_p, aug_min=aug_min, aug_max=aug_max, tokenizer=tokenizer, 
            reverse_tokenizer=reverse_tokenizer, device='cpu', verbose=verbose, include_detail=False)

        self.reserved_tokens = reserved_tokens
        self.reserved_lower_tokens = []
        self.case_sensitive = case_sensitive

        self.reserved_token_dict = {}
        self.reserved_phrase_dict = {}
        self.reserved_phrase_concats = []
        self.reserved_phrase_regexs = []

        if not case_sensitive:
            self.reserved_lower_tokens = [t.lower() for tokens in reserved_tokens for t in tokens]

        reserved_phrase_dict_by_len = defaultdict(list)
        for i, tokens in enumerate(reserved_tokens):
            for t in tokens:
                if not case_sensitive:
                    t = t.lower()

                phrase_tokens = self.tokenizer(t)
                if len(phrase_tokens) == 1:
                    # For single word
                    # If duplicates word occurs, pick the last one.
                    self.reserved_token_dict[t] = i
                else:
                    # For phrase
                    reserved_phrase_dict_by_len[len(phrase_tokens)].append((t, phrase_tokens, i))

        for i in sorted(reserved_phrase_dict_by_len.keys(), reverse=True):
            for phrase, phrase_tokens, pos in reserved_phrase_dict_by_len[i]:
                phrase_concat_token = self.CONNECT_TOKEN.join(phrase_tokens)
                phrase_token_regex = re.compile('(' + phrase + ')', re.IGNORECASE)

                self.reserved_phrase_dict[phrase_concat_token] = pos
                self.reserved_phrase_concats.append(phrase_concat_token)
                self.reserved_phrase_regexs.append(phrase_token_regex)

    def skip_aug(self, token_idxes, tokens):
        # https://arxiv.org/pdf/2007.02033.pdf
        results = []
        for idx in token_idxes:
            t = tokens[idx]
            if not self.case_sensitive:
                t = t.lower()

            if t in self.reserved_token_dict:
                # For single word
                results.append(idx)
            elif t in self.reserved_phrase_dict:
                # For phrase
                results.append(idx)
            
        return results

    def preprocess(self, data):
        for reserved_concat_phrase, reserved_phrase_regex in zip(
            self.reserved_phrase_concats, self.reserved_phrase_regexs):
            data = reserved_phrase_regex.sub(reserved_concat_phrase, data)
        return data

    def substitute(self, data):
        change_seq = 0
        data = self.preprocess(data)
        doc = Doc(data, self.tokenizer(data))

        aug_idxes = self._get_aug_idxes(doc.get_original_tokens())
        aug_idxes.sort(reverse=True)

        tokens = doc.get_original_tokens()

        if aug_idxes is None or len(aug_idxes) == 0:
            if self.include_detail:
                return data, []
            return data

        for aug_idx in aug_idxes:
            original_token = doc.get_token(aug_idx).orig_token.token
            if not self.case_sensitive:
                original_token = original_token.lower()

            if original_token in self.reserved_token_dict:
                candidate_tokens = []
                for t in self.reserved_tokens[self.reserved_token_dict[original_token]]:
                    compare_token = t.lower() if not self.case_sensitive else t
                    if compare_token != original_token:
                        candidate_tokens.append(t)
            elif original_token in self.reserved_phrase_concats:
                candidate_tokens = []
                for t in self.reserved_tokens[self.reserved_phrase_dict[original_token]]:
                    compare_token = t.replace(' ', self.CONNECT_TOKEN)
                    compare_token = compare_token.lower() if not self.case_sensitive else compare_token
                    if compare_token != original_token:
                        candidate_tokens.append(t)

            new_token = self.sample(candidate_tokens, 1)[0]
            if aug_idx == 0:
                new_token = self.align_capitalization(original_token, new_token)

            change_seq += 1
            doc.add_change_log(aug_idx, new_token=new_token, action=Action.SUBSTITUTE, change_seq=self.parent_change_seq+change_seq)

        if self.include_detail:
            return self.reverse_tokenizer(doc.get_augmented_tokens()), doc.get_change_logs()
        else:
            return self.reverse_tokenizer(doc.get_augmented_tokens())

