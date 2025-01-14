import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | S Conj S | S Conj NP | S Conj VP NP
AP -> Adj | Adj AP
NP -> N | Det NP | AP NP | N PP
PP -> P NP
VP -> V | V NP | V NP PP | V PP | Adv VP | VP Adv
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """

    # Tokenize full sentence, giving list of strings
    tokens = nltk.word_tokenize(sentence)

    # Make lowercase and remove non-alpha words, punctuation etc
    processed = [word.lower() for word in tokens if word.isalpha()]

    return processed


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    chunks = []

    # Flag to track if we should keep the subtree or discard
    keep_chunk = True

    # Iterate over all the subtrees of tree that have label NP
    for subtree in tree.subtrees(lambda tree: tree.label() == "NP"):
        # print("Subtree")
        # subtree.pretty_print()
        # We need to check if sub subtrees contain any NP
        # Iterate over sub subtrees and initially set keep_chunk to true
        # If we find any sub subtrees with NP label we can discard this subtree
        for sub_subtree in subtree.subtrees(lambda subtree: subtree.label() == "NP"):
            keep_chunk = True
            if sub_subtree != subtree:
                # print("Sub Subtree")
                # sub_subtree.pretty_print()
                keep_chunk = False
        if keep_chunk:
            chunks.append(subtree)

    return chunks


if __name__ == "__main__":
    main()
