import os

# Unit tests must not download/load the ~GB local TabPFN model or hit the network.
# classify() falls back to the labeled rules path when TabPFN is disabled, which is
# what the classifier/adjudicator unit tests exercise. Live TabPFN is proven separately.
os.environ.setdefault("TABPFN_DISABLE", "1")
