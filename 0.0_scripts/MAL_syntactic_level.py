# SYNTACTIC LEVEL
# sentence, clause and phrase as constructs


import pandas as pd
import MAL_xfy as xfy
import MAL_UD_parser


# AUXILIARY FUNCTION
def count_characters(word):
    """counts characters of all children belonging to a given word"""

    character_n = 0

    for child in word.all_children:
        character_n += len(child.form)

    return character_n


def create_string(a_word_list):
    """takes a list of word nodes and returns a string containing their word forms"""

    word_form_string = ""

    for word_node in a_word_list:
        word_form_string = word_form_string + word_node.form + '+'

    return word_form_string


def stringify_non_clausal_children(direct_children):
    """recursively creates a string of all children which do not belong to other clauses (==CUTS)"""

    clause_words = ""

    for child in direct_children:
        if child.comment != "clause":
            clause_words += child.form + "+"
            clause_words += stringify_non_clausal_children(child.direct_children)

    return clause_words


def list_non_clausal_children(direct_children):
    """recursively creates a list of all children (==nodes) which do not belong to other clauses (==CUTS)"""

    clause_words = []

    for child in direct_children:
        if child.comment != "clause":
            clause_words.append(child)
            clause_words += list_non_clausal_children(child.direct_children)

    return clause_words


def count_non_clausal_children(direct_children):
    """recursively counts all children which do not belong to other clauses (==CUTS)"""

    children_n = 0

    for child in direct_children:
        if child.comment != "clause":
            children_n += 1
            children_n += count_non_clausal_children(child.direct_children)

    return children_n


def count_non_clausal_children_length(direct_children):
    """recursively counts characters of all children (==their lengths) which do not belong to other clauses (==CUTS)"""

    children_length = 0

    for child in direct_children:
        if child.comment != "clause":
            children_length += len(child.form)
            children_length += count_non_clausal_children_length(child.direct_children)

    return children_length


def contain_ascii(a_node_list):
    """detects if a word contains ascii letters U+0000-U+007F -> basic Latin"""

    for node in a_node_list:
        for letter in node.form:
            if letter.isascii():
                return True

    return False


def check_clausal_children(a_word):
    """checks whether any of direct children (==word node) is commented as 'clause'"""

    for child in a_word.direct_children:
        if child.comment != 'clause':
            return True  # can be processed because it governs a non-clausal phrase

    return False  # cannot be processed because it only governs other clauses


def identify_1CS(a_word_list):
    """identifies one-clause sentences"""

    clause_n = 0

    for word in a_word_list:
        if word.comment == 'clause':
            clause_n += 1

    if clause_n == 1:
        return True
    else:
        return False


def process_types(input_file, output_file, column_name):
    """loads quantified data of word tokens, drops duplicates, saves quantified data for phrase types"""

    token_df = pd.read_csv(input_file, delimiter='\t')
    type_df = token_df.drop_duplicates(subset=[column_name])
    type_df.to_csv(path_or_buf=output_file, sep='\t', index=False)


# CORE FUNCTIONS ACCORDING TO LEVELS
#____________________________________________________________________________SENTENCE____________________________________________________________________________#
def sentence_clause_word_cut(a_treebank, weighted_avg_limit):
    """quantifies a UD treebank on the sentence level, creates files with data quantification, xfy for original and weighted values,
       x==sentence length in the number of clauses, f(x)==its frequency, y==clause length in the number of words"""

    clause_n = 0  # number of words commented as 'clause'
    word_n = 0  # number of all root's children + root

    with open('sentence_clause_word_cut.txt', mode='w', encoding='utf-8') as output:
        print('sent_id' + '\t' + 'sent_text' + '\t' + 'clause_n' + '\t' + 'word_n', file=output)  # header

        for sentence in a_treebank.sentence_list:
            for word in sentence.word_list:
                if word.comment == 'clause':
                    clause_n += 1
                if word.deprel == 'root':
                    word_n = len(word.all_children) + 1  # including itself
            print(sentence.id + '\t' + sentence.text + '\t' + str(clause_n) + '\t' + str(word_n), file=output)
            clause_n = 0

    xfy.calculate_xfy('sentence_clause_word_cut.txt', 'sentence_clause_word_cut_xfy.txt', 'clause_n', 'word_n')
    xfy.calculate_weighted_xfy('sentence_clause_word_cut_xfy.txt', 'sentence_clause_word_cut_xfy_weighted.txt', weighted_avg_limit)


def sentence_phrase_word(a_treebank, weighted_avg_limit):
    """quantifies a UD treebank on the sentence level, creates files with data quantification, xfy for original and weighted values,
       x==sentence length in the number of phrases, f(x)==its frequency, y==phrase length in the number of words"""

    phrase_n = 0  # number of root's direct children
    word_n = 0  # number of root's all children

    with open('sentence_phrase_word.txt', mode='w', encoding='utf-8') as output:
        print('sent_id' + '\t' + 'sent_text' + '\t' + 'phrase_n' + '\t' + 'word_n', file=output)  # header

        for sentence in a_treebank.sentence_list:
            for word in sentence.word_list:
                if word.deprel == 'root':
                    phrase_n = len(word.direct_children)
                    word_n = len(word.all_children)  # excluding root
                    print(sentence.id + '\t' + sentence.text + '\t' + str(phrase_n) + '\t' + str(word_n), file=output)

    xfy.calculate_xfy('sentence_phrase_word.txt', 'sentence_phrase_word_xfy.txt', 'phrase_n', 'word_n')
    xfy.calculate_weighted_xfy('sentence_phrase_word_xfy.txt', 'sentence_phrase_word_xfy_weighted.txt', weighted_avg_limit)


def sentence_clause_phrase_cut(a_treebank, weighted_avg_limit):
    """quantifies a UD treebank on the sentence level, creates files with data quantification, xfy for original and weighted values,
       x==sentence length in the number of clauses, f(x)==its frequency, y==clause length in the number of phrases,
       restriction -> clause != phrase applied (==CUTS),
       APPROACH 1: clauses with 0 phrase included -> clause_n += 1 & phrase_n += 0,
       APPROACH 2: clauses with 0 phrase excluded -> clause_n += 0 & phrase_n += 0"""

    clause_n = 0  # number of words commented as 'clause'
    phrase_n = 0  # number of direct children of the words commented as 'clause'

    with open('sentence_clause_phrase_cut.txt', mode='w', encoding='utf-8') as output:
        print('sent_id' + '\t' 'sent_text' + '\t' + 'clause_n' + '\t' + 'c_phrase_n', file=output)  # header

        for sentence in a_treebank.sentence_list:
            for word in sentence.word_list:
                # APPROACH 1 -> if word.comment == 'clause':
                # APPROACH 2 -> if word.comment == 'clause' and len(word.direct_children) != 0 and check_clausal_children(word):
                if word.comment == 'clause':
                    clause_n += 1
                    for child in word.direct_children:
                        if child.comment != 'clause':
                            phrase_n += 1
            print(sentence.id + '\t' + sentence.text + '\t' + str(clause_n) + '\t' + str(phrase_n), file=output)
            clause_n = 0
            phrase_n = 0

    xfy.calculate_xfy('sentence_clause_phrase_cut.txt', 'sentence_clause_phrase_cut_xfy.txt', 'clause_n', 'c_phrase_n')
    xfy.calculate_weighted_xfy('sentence_clause_phrase_cut_xfy.txt', 'sentence_clause_phrase_cut_xfy_weighted.txt', weighted_avg_limit)
#____________________________________________________________________________theend____________________________________________________________________________#


#____________________________________________________________________________CLAUSE____________________________________________________________________________#
def clause_word_character_cut(a_treebank, weighted_avg_limit):
    """quantifies a UD treebank on the clause level, creates files with data quantification, xfy for original and weighted values,
       x==clause length in the number of words, f(x)==its frequency, y==word length in the number of characters,
       each clause is processed separately (==CUTS)"""

    word_n = 0  # number of all children of a word commented as 'clause' and not belonging to other clauses + clausal head
    character_n = 0  # length of all children of the word commented as 'clause' and not belonging to other clauses + clausal head

    with open('clause_word_character_cut.txt', mode='w', encoding='utf-8') as output:
        print('sent_id' + '\t' + 'clause_text' + '\t' + 'word_n' + '\t' + 'character_n', file=output)  # header

        for sentence in a_treebank.sentence_list:
            for word in sentence.word_list:
                if word.comment == 'clause':
                    clause_words = stringify_non_clausal_children(word.direct_children)
                    clause_words += word.form
                    clause_nodes = list_non_clausal_children(word.direct_children)
                    clause_nodes.append(word)
                    # for excluding clauses with non-Chinese graphemes ->  if not contain_ascii(clause_nodes):
                    word_n = len(clause_nodes)
                    character_n = count_non_clausal_children_length(word.direct_children)
                    character_n += len(word.form)  # including itself=head
                    print(sentence.id + '\t' + clause_words + '\t' + str(word_n) + '\t' + str(character_n), file=output)
                word_n = 0
                character_n = 0

    xfy.calculate_xfy('clause_word_character_cut.txt', 'clause_word_character_cut_xfy.txt', 'word_n', 'character_n')
    xfy.calculate_weighted_xfy('clause_word_character_cut_xfy.txt', 'clause_word_character_cut_xfy_weighted.txt', weighted_avg_limit)


def clause_phrase_word_cut(a_treebank, weighted_avg_limit):
    """quantifies a UD treebank on the clause level, creates files with data quantification, xfy for original and weighted values,
       x==clause length in the number of phrases, f(x)==its frequency, y==phrase length in the number of words,
       restriction clause != phrase applied (==CUTS),
       APPROACH 1: excluding clausal heads -> word_n += 0,
       APPROACH 2: including clausal heads -> word_n += 1"""

    phrase_n = 0  # number of direct children of a word commented as 'clause' (excluding other clauses)
    word_n = 0  # number of all children of the word commented as 'clause' (excluding other clauses)

    with open('clause_phrase_word_cut.txt', mode='w', encoding='utf-8') as output:
        print('sent_id' + '\t' + 'clause_text' + '\t' + 'c_phrase_n' + '\t' + 'word_n', file=output)  # header

        for sentence in a_treebank.sentence_list:
            for word in sentence.word_list:
                if word.comment == 'clause':
                    clause_words = stringify_non_clausal_children(word.direct_children)  # excluding clausal heads
                    for child in word.direct_children:
                        if child.comment != 'clause':
                            phrase_n += 1  # excluding clausal heads
                    # APPROACH 1: word_n = count_non_clausal_children(word.direct_children)
                    # APPROACH 2: word_n = count_non_clausal_children(word.direct_children)
                    word_n = count_non_clausal_children(word.direct_children)
                    print(sentence.id + '\t' + clause_words + '\t' + str(phrase_n) + '\t' + str(word_n), file=output)
                    phrase_n = 0

    xfy.calculate_xfy('clause_phrase_word_cut.txt', 'clause_phrase_word_cut_xfy.txt', 'c_phrase_n', 'word_n')
    xfy.calculate_weighted_xfy('clause_phrase_word_cut_xfy.txt', 'clause_phrase_word_cut_xfy_weighted.txt', weighted_avg_limit)
#____________________________________________________________________________theend____________________________________________________________________________#


#____________________________________________________________________________PHRASE____________________________________________________________________________#
def s_phrase_word_character(a_treebank, weighted_avg_limit):
    """quantifies a UD treebank on the phrase level, creates files with data quantification, xfy for original and weighted values,
       x==sentential phrase length in the number of words, f(x)==its frequency, y==word length in the number of characters"""

    word_n = 0  # number of all children of a root
    character_n = 0  # sum of characters of all root's children

    with open('s_phrase_word_character.txt', mode='w', encoding='utf-8') as output:
        print('sent_id' + '\t' 'phrase_text' + '\t' + 'word_n' + '\t' + 'character_n', file=output)  # header

        for sentence in a_treebank.sentence_list:
            for word in sentence.word_list:
                if word.deprel == 'root':  # if a root does not have any children, no record is created
                    for child in word.direct_children:
                        phrase_words = child.form + '+' + create_string(child.all_children)
                        word_n = len(child.all_children) + 1  # including phrasal head
                        character_n = count_characters(child) + len(child.form)
                        print(sentence.id + '\t' + phrase_words + '\t' + str(word_n) + '\t' + str(character_n), file=output)

    xfy.calculate_xfy('s_phrase_word_character.txt', 's_phrase_word_character_xfy.txt', 'word_n', 'character_n')
    xfy.calculate_weighted_xfy('s_phrase_word_character_xfy.txt', 's_phrase_word_character_xfy_weighted.txt', weighted_avg_limit)


def c_phrase_word_character_cut(a_treebank, weighted_avg_limit):
    """quantifies a UD treebank on the phrase level while taking tokens and types into account,
       creates files with data quantification, xfy for original and weighted values,
       x==clausal phrase length in the number of words, f(x)==its frequency, y==word length in the number of characters,
       restriction -> clause != phrase applied (==CUTS)"""

    word_n = 0  # number of all children of a non-clausal child of a word commented as 'clause' including the child (=phrasal head)
    character_n = 0  # sum of characters of all the children including the child (=phrasal head)

    # tokens
    with open('c_phrase_word_character_cut.txt', mode='w', encoding='utf-8') as output:
        print('sent_id' + '\t' + 'phrase_text' + '\t' + 'word_n' + '\t' + 'character_n', file=output)  # header

        for sentence in a_treebank.sentence_list:
            for word in sentence.word_list:
                if word.comment == 'clause':
                    for child in word.direct_children:
                        if child.comment != 'clause':
                            phrase_words = list_non_clausal_children(child.direct_children)
                            phrase_words.append(child)
                            c_phrase_text = create_string(phrase_words)
                            # for excluding phrases with non-Chinese graphemes -> if not contain_ascii(phrase_words):
                            word_n = len(phrase_words)  # including phrasal head
                            character_n = count_non_clausal_children_length(child.direct_children) + len(child.form)  # including phrasal head
                            print(sentence.id + '\t' + c_phrase_text + '\t' + str(word_n) + '\t' + str(character_n), file=output)

    xfy.calculate_xfy('c_phrase_word_character_cut.txt', 'c_phrase_word_character_cut_xfy.txt', 'word_n', 'character_n')
    xfy.calculate_weighted_xfy('c_phrase_word_character_cut_xfy.txt', 'c_phrase_word_character_cut_xfy_weighted.txt', weighted_avg_limit)

    # types
    process_types('c_phrase_word_character_cut.txt', 'c_phrase_word_character_cut_type.txt', 'phrase_text')
    xfy.calculate_xfy('c_phrase_word_character_cut_type.txt', 'c_phrase_word_character_cut_type_xfy.txt', 'word_n', 'character_n')
    xfy.calculate_weighted_xfy('c_phrase_word_character_cut_type_xfy.txt', 'c_phrase_word_character_cut_type_xfy_weighted.txt', weighted_avg_limit)
#____________________________________________________________________________theend____________________________________________________________________________#


#______________________________________________________________________________LDS_____________________________________________________________________________#
def process_lds(a_clausal_head):
    """identifies a segment which words are linearly and syntactically connected"""

    clausal_lds = []
    current_lds = []
    clausal_nodes = list_non_clausal_children(a_clausal_head.direct_children)

    # if a clausal head is the only clausal node
    if len(clausal_nodes) == 0:
        current_lds.append(a_clausal_head)
        clausal_lds.append(current_lds)
        return clausal_lds

    # if a clause includes more than one node
    clausal_nodes.append(a_clausal_head)  # a list of all clausal nodes including the clausal head
    clausal_nodes.sort(key=lambda word_node: word_node.id)  # sorts the list according to ID of nodes in the ascending order

    for i in range(len(clausal_nodes) - 1):

        current_node = clausal_nodes[i]

        while current_node.next_node.deprel == 'punct':
            current_node = current_node.next_node

        # if a next node == linear neighbour and child
        if current_node.next_node == clausal_nodes[i + 1] and clausal_nodes[i].id == clausal_nodes[i + 1].parentID:
            current_lds.append(clausal_nodes[i])
        # if a next node == linear neighbour and parent
        elif current_node.next_node == clausal_nodes[i + 1] and clausal_nodes[i].parentID == clausal_nodes[i + 1].id:
            current_lds.append(clausal_nodes[i])
        # none of the conditions applies -> close a segment
        else:
            current_lds.append(clausal_nodes[i])
            clausal_lds.append(current_lds)
            current_lds = []

    # processes the last node of the clause (==renegade)
    current_lds.append(clausal_nodes[-1])
    clausal_lds.append(current_lds)

    return clausal_lds


def sentence_clause_lds_cut(a_treebank, weighted_avg_limit):
    """quantifies a UD treebank on the sentence level, creates files with data quantification, xfy for original and weighted values,
       x==sentence length in the number of clauses, f(x)==its frequency, y==clause length in the number of lds"""

    clause_n = 0  # number of words commented as 'clause'
    lds_n = 0  # number of lds

    with open('sentence_clause_lds_cut.txt', mode='w', encoding='utf-8') as output:
        print('sent_id' + '\t' + 'sent_text' + '\t' + 'clause_n' + '\t' + 'lds_n', file=output)  # header

        for sentence in a_treebank.sentence_list:
            for word in sentence.word_list:
                if word.comment == 'clause':
                    clause_n += 1
                    lds_n += len(process_lds(word))
            print(sentence.id + '\t' + sentence.text + '\t' + str(clause_n) + '\t' + str(lds_n), file=output)
            clause_n = 0
            lds_n = 0

    xfy.calculate_xfy('sentence_clause_lds_cut.txt', 'sentence_clause_lds_cut_xfy.txt', 'clause_n', 'lds_n')
    xfy.calculate_weighted_xfy('sentence_clause_lds_cut_xfy.txt', 'sentence_clause_lds_cut_xfy_weighted.txt', weighted_avg_limit)


def clause_lds_word_cut(a_treebank, weighted_avg_limit):
    """quantifies a UD treebank on the clause level, creates files with data quantification, xfy for original and weighted values,
       x==clause length in the number of lds, f(x)==its frequency, y==lds length in the number of words"""

    lds_n = 0  # number of lds excluding other clauses
    word_n = 0  # number of all children of clause excluding other clauses

    with open('clause_lds_word_cut.txt', mode='w', encoding='utf-8') as output:
        print('sent_id' + '\t' + 'clause_text' + '\t' + 'lds_n' + '\t' + 'word_n', file=output)  # header

        for sentence in a_treebank.sentence_list:
            for word in sentence.word_list:
                if word.comment == 'clause':
                    clause_words = word.form + '+' + stringify_non_clausal_children(word.direct_children)  # including clausal head
                    lds_n = len(process_lds(word))
                    word_n = count_non_clausal_children(word.direct_children) + 1  # including clausal head
                    print(sentence.id + '\t' + clause_words + '\t' + str(lds_n) + '\t' + str(word_n), file=output)
                    lds_n = 0
                    word_n = 0

    xfy.calculate_xfy('clause_lds_word_cut.txt', 'clause_lds_word_cut_xfy.txt', 'lds_n', 'word_n')
    xfy.calculate_weighted_xfy('clause_lds_word_cut_xfy.txt', 'clause_lds_word_cut_xfy_weighted.txt', weighted_avg_limit)


# def clause_lds_word_sud(a_treebank, weighted_avg_limit):
#     """quantifies a UD treebank on the clause level, creates files with data quantification, xfy for original and weighted values,
#        x==clause length in the number of lds, f(x)==its frequency, y==lds length in the number of words,
#        processes  one-clause sentences in UD and SUD samples"""

#     lds_n = 0  # number of lds excluding other clauses
#     word_n = 0  # number of all children of clause excluding other clauses

#     one_clause_sentences = []

#     with open('clause_lds_word_cut_ud.txt', mode='w', encoding='utf-8') as ud_output:
#         print('sent_id' + '\t' + 'clause_text' + '\t' + 'lds_n' + '\t' + 'word_n', file=ud_output)  # header

#         for sentence in a_treebank.sentence_list:
#             if identify_1CS(sentence.word_list):
#                 one_clause_sentences.append(sentence.id)
#                 for word in sentence.word_list:
#                     if word.deprel == 'root':
#                         clause_words = word.form + '+' + stringify_non_clausal_children(word.direct_children)  # including clausal head
#                         lds_n = len(process_lds(word))
#                         word_n = count_non_clausal_children(word.direct_children) + 1 # including clausal head
#                         print(sentence.id + '\t' + clause_words + '\t' + str(lds_n) + '\t' + str(word_n), file=ud_output)
#                         lds_n = 0
#                         word_n = 0

#     xfy.calculate_xfy('clause_lds_word_cut_ud.txt', 'clause_lds_word_cut_ud_xfy.txt', 'lds_n', 'word_n')
#     xfy.calculate_weighted_xfy('clause_lds_word_cut_ud_xfy.txt', 'clause_lds_word_cut_ud_xfy_weighted.txt', weighted_avg_limit)

#     # name or directory of a treebank file has to be changed accordingly
#     sud_treebank = MAL_UD_parser.create_treebank('zh_gsdsimp-sud-train.conllu')

#     with open('clause_lds_word_cut_sud.txt', mode='w', encoding='utf-8') as sud_output:
#         print('sent_id' + '\t' + 'clause_text' + '\t' + 'lds_n' + '\t' + 'word_n', file=sud_output)  # header

#         for sentence in sud_treebank.sentence_list:
#             if sentence.id in one_clause_sentences:
#                 for word in sentence.word_list:
#                     if word.deprel == 'root':
#                         clause_words = word.form + '+' + stringify_non_clausal_children(word.direct_children)  # including clausal head
#                         lds_n = len(process_lds(word))
#                         word_n = count_non_clausal_children(word.direct_children) + 1 # including clausal head
#                         print(sentence.id + '\t' + clause_words + '\t' + str(lds_n) + '\t' + str(word_n), file=sud_output)
#                         lds_n = 0
#                         word_n = 0

#     xfy.calculate_xfy('clause_lds_word_cut_sud.txt', 'clause_lds_word_cut_sud_xfy.txt', 'lds_n', 'word_n')
#     xfy.calculate_weighted_xfy('clause_lds_word_cut_sud_xfy.txt', 'clause_lds_word_cut_sud_xfy_weighted.txt', weighted_avg_limit)


def lds_word_character_cut(a_treebank, weighted_avg_limit):
    """quantifies a UD treebank on the phrase level while taking tokens and types into account,
       creates files with data quantification, xfy for original and weighted values,
       x==lds length in the number of words, f(x)==its frequency, y==word length in the number of characters"""

    word_n = 0  # number of words
    character_n = 0  # sum of characters of all words in lds

    # tokens
    with open('lds_word_character_cut.txt', mode='w', encoding='utf-8') as output:
        print('sent_id' + '\t' + 'lds_text' + '\t' + 'word_n' + '\t' + 'character_n', file=output)  # header

        for sentence in a_treebank.sentence_list:
            for word in sentence.word_list:
                if word.comment == 'clause':
                    lds_list = process_lds(word)
                    for lds in lds_list:
                        # for excluding phrases with non-Chinese graphemes -> if not contain_ascii(lds):
                        word_n = len(lds)
                        lds_text = ''
                        for lds_word in lds:
                            character_n += len(lds_word.form)
                            lds_text = lds_text + lds_word.form + '+'
                        print(sentence.id + '\t' + lds_text + '\t' + str(word_n) + '\t' + str(character_n), file=output)
                        word_n = 0
                        character_n = 0

    xfy.calculate_xfy('lds_word_character_cut.txt', 'lds_word_character_cut_xfy.txt', 'word_n', 'character_n')
    xfy.calculate_weighted_xfy('lds_word_character_cut_xfy.txt', 'lds_word_character_cut_xfy_weighted.txt', weighted_avg_limit)

    # types
    process_types('lds_word_character_cut.txt', 'lds_word_character_cut_type.txt', 'lds_text')
    xfy.calculate_xfy('lds_word_character_cut_type.txt', 'lds_word_character_cut_type_xfy.txt', 'word_n', 'character_n')
    xfy.calculate_weighted_xfy('lds_word_character_cut_type_xfy.txt', 'lds_word_character_cut_type_xfy_weighted.txt', weighted_avg_limit)
#____________________________________________________________________________theend____________________________________________________________________________#


#__________________________________________________________________________PUNCTUATION_________________________________________________________________________#
def sentence_clause_word_punct(a_treebank, weighted_avg_limit):
    """quantifies a UD treebank on the sentence level, creates files with data quantification, xfy for original and weighted values,
       x==sentence length in the number of clauses, f(x)==its frequency, y==clause length in the number of words,
       the clause is determined based on punctuation marks"""

    clause_n = 0  # number of particular punctuation marks
    word_n = 0  # number of all root's children including itself

    clausal_punctuation = ['，', '：', '；', '…', '……']

    with open('sentence_clause_word_punct.txt', mode='w', encoding='utf-8') as output:
        print('sent_id' + '\t' + 'sent_text' + '\t' + 'clause_n' + '\t' + 'word_n', file=output)  # header

        for sentence in a_treebank.sentence_list:
            clause_n += 1  # including the main clause
            for word in sentence.word_list:
                if word.deprel == 'punct' and word.form in clausal_punctuation:
                    clause_n += 1
                if word.deprel == 'root':
                    word_n = len(word.all_children) + 1  # including itself
            print(sentence.id + '\t' + sentence.text + '\t' + str(clause_n) + '\t' + str(word_n), file=output)
            clause_n = 0

    xfy.calculate_xfy('sentence_clause_word_punct.txt', 'sentence_clause_word_punct_xfy.txt', 'clause_n', 'word_n')
    xfy.calculate_weighted_xfy('sentence_clause_word_punct_xfy.txt', 'sentence_clause_word_punct_xfy_weighted.txt', weighted_avg_limit)


def clause_word_character_punct(a_treebank, weighted_avg_limit):
    """quantifies a UD treebank on the clausal level, creates files with data quantification, xfy for original and weighted values,
       x==clause length in the number of words, f(x)==its frequency, y==word length in the number of characters,
       the clause is determined based on punctuation marks"""

    word_n = 0  # number of words between punctuation marks
    character_n = 0  # length of words between punctuation marks

    clausal_punctuation = ['，', '：', '；', '…', '……']
    clausal_nodes = []

    with open('clause_word_character_punct.txt', mode='w', encoding='utf-8') as output:
        print('sent_id' + '\t' + 'clause_text' + '\t' + 'word_n' + '\t' + 'character_n', file=output)  # header

        for sentence in a_treebank.sentence_list:
            for word in sentence.word_list:
                if word.deprel != 'punct':
                    clausal_nodes.append(word)
                elif (word.form in clausal_punctuation and len(clausal_nodes) != 0) or word.next_node is None:  # last node
                    clause = ''
                    word_n = len(clausal_nodes)
                    for node in clausal_nodes:
                        character_n += len(node.form)
                        clause += node.form
                    print(sentence.id + '\t' + clause + '\t' + str(word_n) + '\t' + str(character_n), file=output)
                    word_n, character_n = 0, 0
                    clausal_nodes = []

    xfy.calculate_xfy('clause_word_character_punct.txt', 'clause_word_character_punct_xfy.txt', 'word_n', 'character_n')
    xfy.calculate_weighted_xfy('clause_word_character_punct_xfy.txt', 'clause_word_character_punct_xfy_weighted.txt', weighted_avg_limit)
#____________________________________________________________________________theend____________________________________________________________________________#
