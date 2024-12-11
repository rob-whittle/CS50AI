from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    Biconditional(AKnight, Not(AKnave)), # If A is a Knight A is not a Knave.  If A is not a Knight it is a Knave.
    Biconditional(AKnight, And(AKnight, AKnave)), # If A is a Knight then the statement "I am both a knight and a knave." is true because Knight never lies.  This is the contridiction the model will check
    # Biconditional(AKnave, Not(And(AKnight, AKnave))) # Knave always lies.  This statement is redundant as the model already know that if A is not a Knight, it must be a Knave
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    Biconditional(AKnight, Not(AKnave)), # Is a Knight if and only if it is not a Knave. We know a knight never lies, so if it is truely a knight it cannot be a knave and vice versa
    Biconditional(BKnight, Not(BKnave)),
    Biconditional(AKnight, And(AKnave, BKnave)) # If A is a Knight then the statement is true, this is the contradiction we test
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    Biconditional(AKnight, Not(AKnave)),
    Biconditional(BKnight, Not(BKnave)),
    # A says "We are the same kind."
    Implication(AKnight, BKnight), # If A is a Knight then implies B is also a knight as always tells the truth
    Implication(AKnave, BKnight),
    # B says "We are of different kinds."
    Implication(BKnight, AKnave),
    Implication(BKnave, AKnave)
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    Biconditional(AKnight, Not(AKnave)),
    Biconditional(BKnight, Not(BKnave)),
    Biconditional(CKnight, Not(CKnave)),
    # C says "A is a knight."
    Implication(CKnight, AKnight),
    Implication(CKnave, AKnave),
    # B says "C is a knave."
    Implication(BKnight, CKnave),
    Implication(BKnave, CKnight),
    # B says "A said 'I am a knave'."
    Implication(BKnight, Not(AKnave))
    # A says either "I am a knight." or "I am a knave.", but you don't know which.
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
