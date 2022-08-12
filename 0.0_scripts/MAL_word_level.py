# WORD LEVEL
# Triplet of word-character-component
# Triplet of word-character-stroke
# Triplet of word-syllable-sound


import pandas as pd
import MAL_word_character_processing as CH
import MAL_word_pinyin_processing as PY
import MAL_xfy as xfy


# AUXILIARY FUNCTION
def contain_ascii(a_word):
    """detects if a word contains ascii letters U+0000-U+007F -> basic latin"""

    for letter in a_word.form:
        if letter.isascii():
            return True

    return False


def count_graphemes(a_syllable_list):
    """counts a word length in the number of graphemes"""

    grapheme_n = 0

    for syllable in a_syllable_list:
        grapheme_n += len(syllable)

    return grapheme_n


def count_all_components(character, metadata_dict):
    """recursively counts all components in a character, i.e. until each component cannot be decomposed further,
       ==maximal decomposition"""

    component_n = 0

    for component in metadata_dict[character]['component']:
        if component in metadata_dict and metadata_dict[component]['component_n'] > 1:
            component_n += count_all_components(component, metadata_dict)
        else:
            component_n += 1

    return component_n


def count_component_stroke(word, metadata_dict):
    """counts a word length in the number of components and strokes"""

    component_n = 0
    stroke_n = 0

    for character in word.form:
        if character in metadata_dict:
            # component_n += count_all_components(character, metadata_dict)  # maximal decomposition
            component_n += metadata_dict[character]['component_n']
            stroke_n += metadata_dict[character]['stroke_n']
        else:  # to detect when data is not available
            return 0, 0

    return component_n, stroke_n


def process_types(input_file, output_file, column_name):
    """loads quantified data of word tokens, drops duplicates, saves quantified data for word types"""

    token_df = pd.read_csv(input_file, delimiter='\t')
    type_df = token_df.drop_duplicates(subset=[column_name])
    type_df.to_csv(path_or_buf=output_file, sep='\t', index=False)


def check_syllables(word):

    for grapheme in word.transliteration:
        if not grapheme.isascii():
            return False

    return True


# CORE FUNCTIONS ACCORDING TO LEVELS
def word_character_component(a_treebank, weighted_avg_limit):
    """quantifies a UD treebank on the word level while taking tokens and types into account,
       creates files with data quantification, xfy for original and weighted values,
       x==word length in the number of characters, f(x)==its frequency, y==character length in the number of components"""

    # choose a source for decomposition of Chinese characters
    character_metadata = CH.create_blcu_dict('hzinfo.txt')
    # character_metadata = CH.create_chise_dictionary('IDS-UCS-Basic.txt')

    # tokens
    with open('word_character_component_token.txt', mode='w', encoding='utf-8') as output:
        print('sent_id' + '\t' + 'word_char' + '\t' + 'character_token_n' + '\t' + 'component_n', file=output)  # header

        for sentence in a_treebank.sentence_list:
            for word in sentence.word_list:
                # UD treebanks:
                # for excluding proper nouns -> and word.upos != 'PROPN':
                if not contain_ascii(word) and word.deprel != 'punct':
                # LCMC:
                # for excluding proper nouns -> and word.upos not in proper_noun_upos:
                # punctuation_upos = ['w', 'ew']
                # proper_noun_upos = ['nr', 'ns', 'nt', 'nz']
                # if not contain_ascii(word) and word.upos not in punctuation_upos:
                    character_n = len(word.form)
                    component_n, stroke_n = count_component_stroke(word, character_metadata)
                    print(sentence.id + '\t' + word.form + '\t' + str(character_n) + '\t' + str(component_n), file=output)

    xfy.calculate_xfy('word_character_component_token.txt', 'word_character_component_token_xfy.txt', 'character_token_n', 'component_n')
    xfy.calculate_weighted_xfy('word_character_component_token_xfy.txt', 'word_character_component_token_xfy_weighted.txt', weighted_avg_limit)

    # types
    process_types('word_character_component_token.txt', 'word_character_component_type.txt', 'word_char')
    xfy.calculate_xfy('word_character_component_type.txt', 'word_character_component_type_xfy.txt', 'character_token_n', 'component_n')
    xfy.calculate_weighted_xfy('word_character_component_type_xfy.txt', 'word_character_component_type_xfy_weighted.txt', weighted_avg_limit)


def word_character_stroke(a_treebank, weighted_avg_limit):
    """quantifies a UD treebank on the word level while taking tokens and types into account,
       creates files with data quantification, xfy for original and weighted values,
       x==word length in the number of characters, f(x)==its frequency, y==character length in the number of strokes"""

    character_metadata = CH.create_blcu_dict('hzinfo.txt')

    # tokens
    with open('word_character_stroke_token.txt', mode='w', encoding='utf-8') as output:
        print('sent_id' + '\t' + 'word_char' + '\t' + 'upos' + '\t' + 'character_token_n' + '\t' + 'stroke_n', file=output)  # header

        for sentence in a_treebank.sentence_list:
            for word in sentence.word_list:
                # UD treebanks:
                # for excluding proper nouns -> and word.upos != 'PROPN':
                if not contain_ascii(word) and word.deprel != 'punct':
                # LCMC:
                # for excluding proper nouns -> and word.upos not in proper_noun_upos:
                # punctuation_upos = ['w', 'ew']
                # proper_noun_upos = ['nr', 'ns', 'nt', 'nz']
                # if not contain_ascii(word) and word.upos not in punctuation_upos:
                    character_n = len(word.form)
                    component_n, stroke_n = count_component_stroke(word, character_metadata)
                    print(sentence.id + '\t' + word.form + '\t' + word.upos + '\t' + str(character_n) + '\t' + str(stroke_n), file=output)

    xfy.calculate_xfy('word_character_stroke_token.txt', 'word_character_stroke_token_xfy.txt', 'character_token_n', 'stroke_n')
    xfy.calculate_weighted_xfy('word_character_stroke_token_xfy.txt', 'word_character_stroke_token_xfy_weighted.txt', weighted_avg_limit)

    # types
    process_types('word_character_stroke_token.txt', 'word_character_stroke_type.txt', 'word_char')
    xfy.calculate_xfy('word_character_stroke_type.txt', 'word_character_stroke_type_xfy.txt', 'character_token_n', 'stroke_n')
    xfy.calculate_weighted_xfy('word_character_stroke_type_xfy.txt', 'word_character_stroke_type_xfy_weighted.txt', weighted_avg_limit)


def word_syllable_sound(a_treebank, weighted_avg_limit):
    """quantifies a UD treebank on the word level while taking tokens and types into account,
       creates files with data quantification, xfy for original and weighted values,
       x==word length in the number of syllables, f(x)==its frequency, y==syllable length in the number of sounds"""

    # tokens
    with open('word_syllable_sound_token.txt', mode='w', encoding='utf-8') as output:
        print('sent_id' + '\t' + 'word_sound' + '\t' + 'word_form' + '\t' + 'upos' + '\t' + 'character_token_n' + '\t' + 'sound_n', file=output)  # header

        for sentence in a_treebank.sentence_list:
            for word in sentence.word_list:
                # UD treebanks:
                # for excluding proper nouns -> and word.upos != 'PROPN':
                if not contain_ascii(word) and word.deprel != 'punct' and word.transliteration is not None:
                # LCMC:
                # for excluding proper nouns -> and word.upos not in proper_noun_upos:
                # punctuation_upos = ['w', 'ew']
                # proper_noun_upos = ['nr', 'ns', 'nt', 'nz']
                # if not contain_ascii(word) and word.upos not in punctuation_upos and word.transliteration is not None and check_syllables(word):
                    character_n = len(word.form)
                    syllable_list = []
                    for syllable in word.transliteration.split(','):
                        syllable_list.append(PY.transform_into_sound(syllable))
                    sound_n = count_graphemes(syllable_list)
                    print(sentence.id + '\t' + str(syllable_list) + '\t' + word.form + '\t' + word.upos + '\t' + str(character_n) + '\t' + str(sound_n), file=output)

    xfy.calculate_xfy('word_syllable_sound_token.txt', 'word_syllable_sound_token_xfy.txt', 'character_token_n', 'sound_n')
    xfy.calculate_weighted_xfy('word_syllable_sound_token_xfy.txt', 'word_syllable_sound_token_xfy_weighted.txt', weighted_avg_limit)

    # types
    process_types('word_syllable_sound_token.txt', 'word_syllable_sound_type.txt', 'word_sound')
    xfy.calculate_xfy('word_syllable_sound_type.txt', 'word_syllable_sound_type_xfy.txt', 'character_token_n', 'sound_n')
    xfy.calculate_weighted_xfy('word_syllable_sound_type_xfy.txt', 'word_syllable_sound_type_xfy_weighted.txt', weighted_avg_limit)
