# MAIN FUNCTIONS


import MAL_UD_parser
import MAL_syntactic_level as S
import MAL_word_level as W
import MAL_character_level as C
import MAL_nlreg as nlr


def export_data(treebank_file):
    """creates a treebank data structure, calls functions for processing given linguistic levels"""

    a_treebank = MAL_UD_parser.create_treebank(treebank_file)
    weighted_avg_limit = 10

    # SYNTACTIC LEVEL
    # sentence level
    S.sentence_clause_word_cut(a_treebank, weighted_avg_limit)
    S.sentence_clause_word_punct(a_treebank, weighted_avg_limit)  # punctuation approach
    S.sentence_phrase_word(a_treebank, weighted_avg_limit)
    S.sentence_clause_phrase_cut(a_treebank, weighted_avg_limit)
    S.sentence_clause_lds_cut(a_treebank, weighted_avg_limit)

    # clause level
    S.clause_word_character_cut(a_treebank, weighted_avg_limit)
    S.clause_word_character_punct(a_treebank, weighted_avg_limit)  # punctuation approach
    S.clause_phrase_word_cut(a_treebank, weighted_avg_limit)
    S.clause_lds_word_cut(a_treebank, weighted_avg_limit)
    # S.clause_lds_word_sud(a_treebank, weighted_avg_limit)  # one-clause sentences in UD and SUD frameworks

    # phrase level
    S.s_phrase_word_character(a_treebank, weighted_avg_limit)
    S.c_phrase_word_character_cut(a_treebank, weighted_avg_limit)
    S.lds_word_character_cut(a_treebank, weighted_avg_limit)

    # WORD LEVEL
    W.word_character_component(a_treebank, weighted_avg_limit)
    W.word_character_stroke(a_treebank, weighted_avg_limit)
    W.word_syllable_sound(a_treebank, weighted_avg_limit)

    # CHARACTER LEVEL
    C.character_component_stroke(a_treebank, weighted_avg_limit)


def process_nlreg_data(filename_list):
    """loops via a list of files containing xfy values of a given triplet of language units,
       creates NLREG program files and output files with results for both (truncated and complete) models"""

    for filename in filename_list:
        # checks content of a file if it is not empty
        if len(nlr.load_xfy_file(filename)) > 1:
            nlr.run_nlreg(filename)


filename_list = ['sentence_clause_word_cut_xfy.txt', 'sentence_clause_word_cut_xfy_weighted.txt',
            'sentence_clause_word_punct_xfy.txt', 'sentence_clause_word_punct_xfy_weighted.txt',
            'sentence_phrase_word_xfy.txt', 'sentence_phrase_word_xfy_weighted.txt',
            'sentence_clause_phrase_cut_xfy.txt', 'sentence_clause_phrase_cut_xfy_weighted.txt',
            'sentence_clause_lds_cut_xfy.txt', 'sentence_clause_lds_cut_xfy_weighted.txt',
            'clause_word_character_cut_xfy.txt', 'clause_word_character_cut_xfy_weighted.txt',
            'clause_word_character_punct_xfy.txt', 'clause_word_character_punct_xfy_weighted.txt',
            'clause_phrase_word_cut_xfy.txt', 'clause_phrase_word_cut_xfy_weighted.txt',
            'clause_lds_word_cut_xfy.txt', 'clause_lds_word_cut_xfy_weighted.txt',
            # 'clause_lds_word_cut_ud_xfy.txt', 'clause_lds_word_cut_ud_xfy_weighted.txt',
            # 'clause_lds_word_cut_sud_xfy.txt', 'clause_lds_word_cut_sud_xfy_weighted.txt',
            's_phrase_word_character_xfy.txt', 's_phrase_word_character_xfy_weighted.txt',
            'c_phrase_word_character_cut_xfy.txt', 'c_phrase_word_character_cut_xfy_weighted.txt',
            'c_phrase_word_character_cut_type_xfy.txt', 'c_phrase_word_character_cut_type_xfy_weighted.txt',
            'lds_word_character_cut_xfy.txt', 'lds_word_character_cut_xfy_weighted.txt',
            'lds_word_character_cut_type_xfy.txt', 'lds_word_character_cut_type_xfy_weighted.txt',
            'word_character_component_token_xfy.txt', 'word_character_component_token_xfy_weighted.txt',
            'word_character_component_type_xfy.txt', 'word_character_component_type_xfy_weighted.txt',
            'word_character_stroke_token_xfy.txt', 'word_character_stroke_token_xfy_weighted.txt',
            'word_character_stroke_type_xfy.txt', 'word_character_stroke_type_xfy_weighted.txt',
            'word_syllable_sound_token_xfy.txt', 'word_syllable_sound_token_xfy_weighted.txt',
            'word_syllable_sound_type_xfy.txt', 'word_syllable_sound_type_xfy_weighted.txt',
            'character_component_stroke_token_xfy.txt', 'character_component_stroke_token_xfy_weighted.txt',
            'character_component_stroke_type_xfy.txt', 'character_component_stroke_type_xfy_weighted.txt']


# Example of calling both the functions above
export_data('zh_pud-ud-test.conllu')
process_nlreg_data(filename_list)
