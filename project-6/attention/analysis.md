# Analysis

## Layer 5, Head 6

This attention head appears to have learned to pay attention to the relationship between determiner and noun.  In the first example sentence we can see a clear relationship learned between the definitive article determiner 'the' and the noun 'fox'.  The second sentance is a little noiser, but there is a clear relationship learned between 'the' and 'butterfly'.

Example Sentences:
- the quick [MASK] fox jumps over the lazy dog
- the cabbage white butterfly lays its [MASK] on members of the Brassica genus

## Layer 5, Head 1

With the first example sentence, this attention head appears to have learned to pay attention to the relationship between verb and adposition - we can see a clear relationship learned between the adposition 'over' and the preceeding verb 'jumps'.  However with the very similar second sentence, no relationship is identified at all!  Perhaps then it is the case that it only learned the relationship between verbs that convey movement and adposition.  I tested this with the third example sentence.  Although not as obvious as the first sentence, there is an indication of a relationship learned between 'under' and crawled.

Example Sentences:
- the quick [MASK] fox jumps over the lazy dog
- the large [MASK] cat sleeps beneath the warm blanket
- the large [MASK] cat crawled under the warm blanket