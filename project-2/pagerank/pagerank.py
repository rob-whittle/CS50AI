import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    # Get linked pages
    linked_pages = corpus[page]

    # if no linked pages then return probability of choosing a random page
    if not linked_pages:
        p = 1 / len(corpus)
        return dict.fromkeys(corpus, p)

    # With probability `1 - damping_factor`, choose
    # a link at random chosen from all pages in the corpus
    p_any = (1 - damping_factor) / len(corpus)

    # create initial distribution where each page has equal probability
    p_dist = dict.fromkeys(corpus, p_any)

    # With probability `damping_factor`, choose a link at random
    # linked to by `page`.
    p_linked = damping_factor * (1 / len(linked_pages))

    # update distribution with probability of clicking linked pages
    for link in linked_pages:
        p_dist[link] += p_linked

    return p_dist

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Create dictonary of page ranks and set rank to zero for all pages
    page_rank = dict.fromkeys(corpus, 0)

    # choose random starting page
    start_page = random.choice(list(corpus.keys()))
    distribution = transition_model(corpus, start_page, damping_factor)

   # add rank for start page
    page_rank[start_page] = 1

    for _ in range(n):
        # choose next page at random considering probability distribution
        next_page = random.choices(population=list(distribution.keys()), weights=list(distribution.values()))
        # record the chosen page.  Note next_page is a single item list
        page_rank[next_page[0]] += 1
        # get new distribution
        distribution = transition_model(corpus, next_page[0], damping_factor)

    # normalise page ranks
    denominator = sum(page_rank.values())
    return {key: (value / denominator) for key, value in page_rank.items()}


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Create dictonary of page ranks and set rank to 1 / N for all pages
    N = len(corpus)
    page_rank = dict.fromkeys(corpus, 1 / N)

    # New dict to update with revised page ranks
    new_page_rank = dict(page_rank)

    # set to keep track of pages that we need to continue to iterate through (because rank is changing still)
    page_tracker = set(corpus.keys())

    while page_tracker:
        # update page_rank to a new copy of new_page_rank so the following loops uses updated page ranks
        page_rank = dict(new_page_rank)

        for page in corpus:
            # if the page is no longer in the tracker then we don't need to iterate it again
            if page not in page_tracker:
                continue

            backlink_ranks = []
            # iterate through the corpus and find all pages that link to current page
            for pg, links in corpus.items():
                # find relative rank of backlinks by dividing the source page rank by number of links to this page
                if page in links:
                    backlink_ranks.append(page_rank[pg] / len(links))
                # if a page has no links at all interpret as having one link for every page in the corpus (including itself)
                elif not links:
                    backlink_ranks.append(page_rank[pg] / N)

            rank = (1 - damping_factor) / N + (damping_factor * sum(backlink_ranks))
            # check if rank changed by more than specified delta
            if abs(rank - page_rank[page]) > 0.001:
                new_page_rank[page] = rank
            else:
                # otherwise remove from further iterations
                page_tracker.remove(page)

    return new_page_rank


if __name__ == "__main__":
    main()
