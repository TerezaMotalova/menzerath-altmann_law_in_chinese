# FUNCTIONS FOR PROCESSING A TREEBANK FILE IN CONLLU FORMAT


class Treebank:

    def __init__(self):
        self.sentence_list = []


class Sentence:

    def __init__(self):
        self.id = None
        self.text = None
        self.root = None
        self.word_list = []


class Word:

    def __init__(self):
        self.id = None
        self.form = None
        self.lemma = None
        self.upos = None
        self.xpos = None
        self.feats = None
        self.parentID = None
        self.parent = None
        self.deprel = None
        self.deps = None
        self.transliteration = None
        self.comment = None
        self.next_node = None
        self.direct_children = []
        self.all_children = []


def create_worddata(a_line):
    """processes data from a word line"""

    new_word = Word()
    word_data = a_line.split('\t')
    new_word.id = int(word_data[0])
    new_word.form = word_data[1].strip()  # strip fc for arbitrary spaces
    new_word.lemma = word_data[2]
    new_word.upos = word_data[3]
    new_word.xpos = word_data[4]
    new_word.feats = word_data[5]
    new_word.parentID = int(word_data[6])
    new_word.deprel = word_data[7]
    new_word.deps = word_data[8]
    if 'Translit' in a_line:
        new_word.transliteration = word_data[9].split('=')[-1].strip().lower()  # strip fc for arbitrary spaces

    return new_word


def load_treebank(filename):
    """opens conllu file, loads data and returns a treebank data structure"""

    a_treebank = Treebank()
    a_sentence = None

    with open(filename, mode='r', encoding='utf-8') as data:
        for line in data:
            if line.startswith('# sent_id'):  # sentence identification
                a_sentence = Sentence()
                a_sentence.id = line.split('=')[1].strip()
                a_treebank.sentence_list.append(a_sentence)
            if line.startswith('# text ='):  # text identification
                a_sentence.text = line.strip()
            if not line.startswith('#') and len(line) > 1:  # reads LF character too
                a_sentence.word_list.append(create_worddata(line))

    return a_treebank


def assign_next_node(a_treebank):
    """adds a next node to word data"""

    for sentence in a_treebank.sentence_list:
        for _ in range(len(sentence.word_list) - 1):
            sentence.word_list[_].next_node = sentence.word_list[_ + 1]

            if (sentence.word_list[_].id + 1) != sentence.word_list[_ + 1].id:
                raise ValueError('ERROR!')

    return a_treebank


def find_parent_and_children(a_treebank):  # NOTE: root parent is None!
    """interlinks the data based on the parent-child relationship"""

    for sentence in a_treebank.sentence_list:
        for word in sentence.word_list:
            if word.parentID != 0 and word.deprel != 'punct':
                word.parent = sentence.word_list[word.parentID - 1]  # assign a parent in the form of a word class
                word.parent.direct_children.append(word)  # add a child to its parent
            else:
                sentence.root = word

    return a_treebank


def add_word_to_all_parents(word, parent):
    """adds a word to all their parents from the bottom to top of the treebank data structure"""

    if parent is not None:
        parent.all_children.append(word)
        add_word_to_all_parents(word, parent.parent)


def find_all_children(a_treebank):
    """finds all nodes directly and indirectly dependent on a given word in the treebank data structure"""

    for sentence in a_treebank.sentence_list:
        for word in sentence.word_list:
            if word.deprel != 'punct':
                add_word_to_all_parents(word, word.parent)

    return a_treebank


def tag_clause_head(a_treebank):
    """adds a clausal comment to words which deprel is one of the below-mention UD dependency relations"""

    clausal_tags = ['root', 'csubj', 'csubj:pass', 'ccomp', 'xcomp', 'advcl', 'acl', 'acl:relcl', 'parataxis']

    for sentence in a_treebank.sentence_list:
        for word in sentence.word_list:
            if word.deprel in clausal_tags:
                word.comment = 'clause'

    return a_treebank


def tag_coordinate_clause(a_treebank):
    """broadens clauses by conj which inherits the clausal comment if its parent is commented as 'clause'"""

    for sentence in a_treebank.sentence_list:
        for word in sentence.word_list:
            if word.deprel == 'conj' and word.parent.comment == 'clause':
                word.comment = 'clause'

    return a_treebank


def create_treebank(filename):
    """combines all the functions and returns a complete treebank data structure"""

    a_treebank = load_treebank(filename)
    a_treebank = assign_next_node(a_treebank)
    a_treebank = find_parent_and_children(a_treebank)
    a_treebank = find_all_children(a_treebank)
    a_treebank = tag_clause_head(a_treebank)
    a_treebank = tag_coordinate_clause(a_treebank)

    return a_treebank
