import logging
log = logging.getLogger("scheme")

from subset import Subset

class SchemeError(Exception):
    pass

class Scheme(object):
    def __init__(self, schemeset, name, subsets):
        """A set of partitions"""
        self.schemeset = schemeset
        self.name = name

        self.subsets = []
        for subset_def in subsets:
            subset_id = self.make_subset_id(subset_def)
            subset = self.schemeset.get_subset(subset_id)
            self.subsets.append(subset)

        # Now check that the scheme is complete...
        all_columns = set()
        for subset in self.subsets:
            all_columns |= subset.columnset

        if all_columns != self.schemeset.partitions.columnset:
            log.error("Scheme '%s' does not contain all partitions", name)
            raise SchemeError

        # Finally, add it to the schemeset
        log.debug("Creating Scheme '%s'", name)
        schemeset.add_scheme(self)

    def make_subset_id(self, subset_def):
        """Check to make sure the partitions exist"""
        parts = self.schemeset.partitions
        for partname in subset_def:
            # Check it is a valid partition
            if partname not in parts:
                log.error(
                    "Creating scheme '%s': '%s' is not a defined partition",
                    name, partname)
                raise SchemeError
        return frozenset(subset_def)

class SchemeSet(object):
    """All the schemes added, and also a list of all unique subsets"""
    def __init__(self, partitions):
        """A collection of schemes"""
        self.partitions = partitions
        self.schemes = {}
        self.subsets = {}

    def get_subset(self, subset_id):
        """Return an existing subset or make a new one"""
        if subset_id in self.subsets:
            return self.subsets[subset_id]

        # Create a new subset
        sub = Subset(self.partitions, subset_id)
        self.subsets[subset_id] = sub
        return sub

    def add_scheme(self, scheme):
        if scheme.name in self.schemes:
            log.error("Cannot add two schemes with same name: '%s'" %
                      scheme.name)
            raise SchemeError
        self.schemes[scheme.name] = scheme
