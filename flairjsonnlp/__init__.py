#!/usr/bin/env python3

"""
(C) 2019 Damir Cavar, Oren Baldinger, Maanvitha Gongalla, Anurag Kumar, Murali Kammili, Boli Fang

Wrappers for Flair to JSON-NLP output format.

Licensed under the Apache License 2.0, see the file LICENSE for more details.

Brought to you by the NLP-Lab.org (https://nlp-lab.org/)!
"""

from collections import OrderedDict
from typing import List, Generator
from flair.data import Sentence
from flair.embeddings import StackedEmbeddings, WordEmbeddings, FlairEmbeddings, CharacterEmbeddings, BytePairEmbeddings
from flair.models import SequenceTagger, TextClassifier
from flair.nn import Model
from nltk import PunktSentenceTokenizer
import jsonnlp # import base_nlp_json, base_document
import functools

name = "flairjsonnlp"

__version__ = "0.0.1"

sentence_tokenizer = PunktSentenceTokenizer()

def cache_it(func):
    """A decorator to cache function response based on params. Add it to top of function as @cache_it."""

    global __cache

    @functools.wraps(func)
    def cached(*args):
        f_name = func.__name__
        s = ''.join(map(str, args))
        if s not in __cache[f_name]:
            __cache[f_name][s] = func(*args)
        return __cache[f_name][s]
    return cached

@cache_it
def get_sequence_model(model_name) -> SequenceTagger:
    return SequenceTagger.load(model_name)


@cache_it
def get_classifier_model(model_name) -> TextClassifier:
    return TextClassifier.load(model_name)


def get_embeddings(embeddings: List[str], character: bool, bpe: str) -> StackedEmbeddings:
    """Construct and return a embedding model"""
    stack = []
    for e in embeddings:
        if e in ('glove',):
            stack.append(WordEmbeddings(e))
        elif e in ('multi-forward', 'multi-backward', 'news-forward', 'news-backward'):
            stack.append(FlairEmbeddings(e))
        elif e is not '':
            raise ModuleNotFoundError(f'{e} embeddings are not currently supported!')
    if character:
        stack.append(CharacterEmbeddings())
    if bpe:
        if bpe not in ('en',):
            raise ModuleNotFoundError(f'{bpe} is not supported for Byte Pair Embeddings')
        stack.append(BytePairEmbeddings(bpe))

    return StackedEmbeddings(embeddings=stack)


def get_models(lang: str, use_ontonotes: bool, fast: bool) -> Generator[Model, None, None]:
    """Yield all relevant models"""
    if lang == 'en':
        yield get_sequence_model('pos-fast' if fast else 'pos')  # xpos
        yield get_sequence_model(('ner-ontonotes' if use_ontonotes else 'ner') + ('-fast' if fast else ''))
        yield get_sequence_model('frame-fast' if fast else 'frame')
        yield get_sequence_model('chunk-fast' if fast else 'chunk')
        yield get_classifier_model('en-sentiment')
    elif lang == 'de':
        yield get_sequence_model('de-pos')  # xpos
        yield get_sequence_model('de-ner-germeval')
        yield get_classifier_model('de-offensive-language')
    elif lang == 'fr':
        yield get_sequence_model('fr-ner')
    elif lang == 'nl':
        yield get_sequence_model('nl-ner')
    else:
        yield get_sequence_model('ner-multi-fast' if fast else 'ner-multi')

    # we always would like universal pos tags
    yield get_sequence_model('pos-multi-fast' if fast else 'pos-multi')


def get_flair_sentences(text, lang, use_ontonotes, fast, use_embeddings, char_embeddings, bpe, d):
    """Process text using Flair and return the output from Flair"""

    if lang not in ('en', 'multi', 'de', 'nl', 'fr'):
        raise TypeError(f'{lang} is not supported! Try multi. See https://github.com/zalandoresearch/flair/blob/master/resources/docs/TUTORIAL_2_TAGGING.md')

    # tokenize sentences and decorate them with all the appropriate model predictions
    sentences = [Sentence(t) for t in sentence_tokenizer.sentences_from_text(text)]
    for model in get_models(lang=lang, use_ontonotes=use_ontonotes, fast=fast):
        model.predict(sentences)

    # load embedding models
    if use_embeddings == 'default':
        use_embeddings = 'glove,multi-forward,multi-backward'
    embed_type = f'Flair {use_embeddings}' + (',char' if char_embeddings else '') + (',byte-pair' if bpe else '')
    if use_embeddings or char_embeddings or bpe:
        get_embeddings([e.strip() for e in use_embeddings.split(',')], char_embeddings, bpe).embed(sentences)

    # sentences
    token_id = 1
    for i, s in enumerate(sentences):
        sent = {
            'id': str(i),
            'tokenFrom': token_id,
            'tokenTo': token_id + len(s),
            'tokens': []
        }
        d['sentences'].append(sent)

        # sentiment and any other classifiers
        for label in s.labels:
            if 'labels' not in sent:
                sent['labels'] = []
            sent['labels'].append({
                'type': 'sentiment' if label.value in ('POSITIVE', 'NEGATIVE') else 'offensive language',
                'label': label.value,
                'scores': {'label': label.score}
            })

        # syntactic chunking (expressions)
        d['expressions'] = [{
            'type': span.tag,
            'scores': {'type': span.score},
            # before tokens are processed, token_id points to the start of this sentence
            # the Token.idx property starts from 1
            'tokens': [t.idx + token_id - 1 for t in span.tokens]
        } for span in s.get_spans('np') if len(span.tokens) > 1]

        # tokens
        for token in s:
            t = {
                'id': token_id,
                'text': token.text,
                'characterOffsetBegin': token.start_pos,
                'characterOffsetEnd': token.end_pos,
                'features': {'Overt': 'Yes'},
                'scores': {},
                'misc': {'SpaceAfter': 'Yes' if token.whitespace_after else 'No'}
            }

            # pos
            pos = token.get_tag('upos')  # 'multi' models give universal pos tags
            if pos.value:
                t['upos'] = pos.value
                t['scores']['upos'] = pos.score
            pos = token.get_tag('pos')
            if pos.value:
                t['xpos'] = pos.value
                t['scores']['xpos'] = pos.score

            # named entities
            entity = token.get_tag('ner')
            if entity.value != 'O':
                t['entity'] = entity.value
                # determine the entity value of the previous token in this sentence
                e = d['tokenList'][-1].get('entity') if token.idx != 1 else None
                t['entity_iob'] = 'B' if e != entity.value else 'I'
                t['scores']['entity'] = entity.score
            else:
                t['entity_iob'] = 'O'

            # semantic frames (wordnet)
            frame = token.get_tag('frame')
            if frame.value:
                # normalize the frame id
                f = frame.value.split('.')
                t['synsets'] = [{
                    'wordnetId': '.'.join([f[0], t['upos'][0].lower(), f[1]]),
                    'scores': {'wordnetId': frame.score}
                }]

            # word embeddings
            if embed_type != 'Flair ':  # some models will add embeddings, but we only want them if requested
                t['embeddings'] = [{
                    'model': embed_type,
                    'vector': token.embedding.tolist()
                }]

            d['tokenList'].append(t)
            sent['tokens'].append(token_id)
            token_id += 1

def get_nlp_json(text, lang, use_ontonotes, fast, use_embeddings, char_embeddings, bpe) -> OrderedDict:
    """Process the Flair output into JSON-NLP"""

    from flair import __version__
    FlairVersion = __version__

    j: OrderedDict = jsonnlp.base_nlp_json()
    j['DC.source'] = f'Flair { FlairVersion }'
    j['DC.language'] = lang
    j['documents'].append(jsonnlp.base_document())
    d = j['documents'][-1]
    d['text'] = text
    get_flair_sentences(text, lang, use_ontonotes, fast, use_embeddings, char_embeddings, bpe, d)
    return j

def process(cache, text: str, lang='en', use_ontonotes=False, fast=True, use_embeddings='', char_embeddings=False, bpe=''):
    """Process the text into JSON-NLP"""
    global __cache
    __cache = cache
    return get_nlp_json(text, lang, use_ontonotes, fast, use_embeddings, char_embeddings, bpe)