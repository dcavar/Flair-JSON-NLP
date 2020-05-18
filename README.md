# Flair JSON-NLP Wrapper

(C) 2019-2020 by [Damir Cavar]

Contributors to previous versions: [Oren Baldinger], [Maanvitha Gongalla], Anurag Kumar, Murali Kammili

Brought to you by the [NLP-Lab.org]!


## Introduction

[Flair] v 4.5 wrapper for [JSON-NLP]. [Flair] provides state-of-the-art embeddings, and tagging capabilities,
in particular, POS-tagging, NER, shallow syntax chunking, and semantic frame detection.


## FlairPipeline

We provide a `FlairPipeline` class, with the following parameters for ease of use:

- `lang`: defaults to `en`. Different languages support different models, see the [Flair Docs] for details.
- `use_ontonotes`: defaults to `False`. Whether or not to use 4-class (True) or 12-class (False) NER tagging.
- `fast`: defaults to `True`. Whether or not to use the smaller, faster, but slightly less accurate versions of the models.
- `use_embeddings`: defaults to ''. Passing `default` will map to `glove,multi-forward,multi-backward`, the recommended stacked-embedding configuration.
- `char_embeddings`: defaults to `False`. Whether or not to include character-level embeddings.
- `bpe_size`: defaults to 0. If you want to include [Byte-Pair Encodings](https://nlp.h-its.org/bpemb/), set this value to 50, 100, 200, or 300. See more at [Flair Embeddings Docs](https://github.com/zalandoresearch/flair/blob/master/resources/docs/TUTORIAL_3_WORD_EMBEDDING.md).
- `pos`: defaults to `True`. Whether or not to include language-specific part-of-speech tags.
- `sentinment`: defaults to `True`. Whether or not to include sentiment analysis, if it is available for the given language.

Tagging and Embedding models are downloaded automatically the first time they are called.
This may take a while depending on your internet connection.


## Microservice

The [JSON-NLP] repository provides a Microservice class, with a pre-built implementation of [Flask]. To run it, execute:
    
    python flairjsonnlp/server.py
 
Since `server.py` extends the [Flask] app, a WSGI file would contain:

    from flairjsonnlp.server import app as application

The microservice exposes the following URIs:
- /expressions
- /token_list

These URIs are shortcuts to disable the other components of the parse. In all cases, `tokenList` will be included in the `JSON-NLP` output. An example url is:

    http://localhost:5000/expressions?text=I am a sentence

Text is provided to the microservice with the `text` parameter, via either `GET` or `POST`. If you pass `url` as a parameter, the microservice will scrape that url and process the text of the website.

The additional [Flair] parameters can be passed as parameters as well.

Here is an example `GET` call:

    http://localhost:5000?lang=de&constituents=0&text=Ich bin ein Berliner.



[Damir Cavar]: http://damir.cavar.me/ "Damir Cavar"
[Oren Baldinger]: https://oren.baldinger.me/ "Oren Baldinger"
[Maanvitha Gongalla]: https://maanvithag.github.io/MaanvithaGongalla/ "Maanvitha Gongalla"
[NLP-Lab.org]: http://nlp-lab.org/ "NLP-Lab.org"
[JSON-NLP]: https://github.com/dcavar/JSON-NLP "JSON-NLP"
[Flair]: https://github.com/zalandoresearch/flair "Flair"
[spaCy]: https://spacy.io/ "spaCy"
[NLTK]: http://nltk.org/ "Natural Language Processing Toolkit"
[Polyglot]: https://github.com/aboSamoor/polyglot "Polyglot" 
[Xrenner]: https://github.com/amir-zeldes/xrenner "Xrenner"
[CONLL-U]: https://universaldependencies.org/format.html "CONLL-U"
[Flask]: http://flask.pocoo.org/ "Flask"
[Flair Docs]: https://github.com/zalandoresearch/flair/tree/master/resources/docs "Flair Docs"
