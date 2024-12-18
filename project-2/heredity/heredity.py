import csv
import itertools
import sys
import math

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    # New dictionary to track probability calcs for each person
    probabilities = dict.fromkeys(people, None)

    for person in people:
        # check if have parents
        mother = people[person]["mother"]
        father = people[person]["father"]

        # set trait to True or False
        trait = person in have_trait

        if father is None and mother is None:
            # calc joint probability of having x gene(s) and trait/no trait
            if person in one_gene:
                p = PROBS["gene"][1] * PROBS["trait"][1][trait]

            elif person in two_genes:
                p = PROBS["gene"][2] * PROBS["trait"][2][trait]

            else:
                p = PROBS["gene"][0] * PROBS["trait"][0][trait]

            # update probability for this person
            probabilities[person] = p

        # if they have parents then need to calc the probability they
        # inherited the gene from parents, rather than using the unconditional
        #  probability
        else:
            p_mother = inherit_gene(mother, one_gene, two_genes)
            p_father = inherit_gene(father, one_gene, two_genes)

            if person in one_gene:
                # if the child has one gene then could come from one and only one parent
                p_inherit = p_mother * (1 - p_father) + p_father * (1 - p_mother)
                p_trait = PROBS["trait"][1][trait]

            elif person in two_genes:
                # if child has two genes, inherit from both parents
                p_inherit = p_mother * p_father
                p_trait = PROBS["trait"][2][trait]

            else:
                # if child has no genes, inherited from neither parent
                p_inherit = (1 - p_mother) * (1 - p_father)
                p_trait = PROBS["trait"][0][trait]

            # update probability for this person
            probabilities[person] = p_inherit * p_trait

    # return the joint probability of the input scenario
    return math.prod(probabilities.values())


def inherit_gene(parent, one_gene, two_genes):
    """
    Calculates the probability that a parent passed gene to child
    """
    if parent in one_gene:
        # 50% chance of passing on faulty gene or 50% chance non-faulty gene mutates
        # 0.5 * (1 - PROBS["mutation"]) + 0.5 * PROBS["mutation"]
        return 0.5
    elif parent in two_genes:
        # the probability the faulty gene did not mutate
        return (1 - PROBS["mutation"])
    else:
        # probability non-faulty gene mutated
        return PROBS["mutation"]


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:

        # trait is True or False
        trait = person in have_trait
        probabilities[person]["trait"][trait] += p

        # update genes
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """

    for person in probabilities:
        # attribute is either "gene" or "trait"
        # distribution is a dictionary defining probability distribution
        for attribute, distribution in probabilities[person].items():
            # the values of distribution can be summed to find the normalisation factor
            denominator = sum(distribution.values())
            # now update each values in the distribution
            for key in distribution:
                probabilities[person][attribute][key] /= denominator


if __name__ == "__main__":
    main()
