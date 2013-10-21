from rdkit.Chem import AllChem
from chemical import Chemical


class Reaction:
    """Represents a reaction."""

    def __init__(self, smiles, rxnid=None, year = 2020):
        """Initialize entry."""
        self.rxnid = rxnid
        self.year = year
        self.smiles = smiles.strip()
        self.react_smis, self.prod_smis = [s.split('.')
                                           for s in self.smiles.split('>>')]
        try:
            self.reactants = [Chemical(smi) for smi in self.react_smis]
            self.products = [Chemical(smi) for smi in self.prod_smis]
        except ValueError:
            raise ValueError('invalid substrates and/or products')

    def __eq__(self, other):
        """Defines equality operator for class instances.

        Reactions B is considered to be equal to reaction A, if its both
        reactant and product SMILES are respective subsets of reaction A's
        reactants and products SMILES.
        """
        return (set(other.react_smis).issubset(self.react_smis) and
                set(other.prod_smis).issubset(self.prod_smis))

    def __ne__(self, other):
        """Defines inequality operator for class instances.

        Reactions A and B are considered unequal when they are not equal.

        Note:
        Although the sentence above may sound like a tautology, defining
        equality operator does *not* automatically add a support for '!='
        operator, it must be added explicitly.
        """
        return not self == other

    def get_descriptors(self):
        """Calculates and returns a list of reaction descriptors.

        Currently, we are using purely molecular descriptors. In an attempt
        use them to characterize a reaction, for each available descriptor,
        we are calculating a total sum its values for all reactants and
        products separately. The resulting pair of numbers is our reaction
        descriptor corresponding to a given molecular descriptor.

        Simple compounds with a single-atom H-depleted molecular graph (e.g.
        water, 'O') are *excluded* from the count as both  adjacency and
        distance matrices on which many topological descriptors rely are
        not well defined (they are just 0) in such a case.
        """

        # If any descriptors should be ignored, put their names in the list
        # below.
        blacklist = []

        results = []
        for name, descriptor in Chemical:
            if name in blacklist:
                continue
            results.append(sum(descriptor(chem) for chem in self.reactants
                               if chem.a.size > 1))
            results.append(sum(descriptor(chem) for chem in self.products
                               if chem.a.size > 1))
        return results

    def get_group_descriptor(self, groups):
        """Return descriptor based on functional group count.

        Function returns a vector which elements indicates how many functional
        group of a given type are present in reaction's reactants.
        """
        group_count = {}
        for chem in self.reactants + self.products:
            for group, count in chem.functional_groups.items():
                group_count.setdefault(group, 0.0)
                group_count[group] += count

        descriptor = []
        for smarts in sorted(groups.keys()):
            descriptor.append(group_count.get(smarts, 0))
        return descriptor


class Transform:
    """Represents retrosynthetic transform."""

    def __init__(self, smarts):
        self.smarts = smarts
        self.retrons, self.synthons = [s.split('.')
                                       for s in smarts.split('>>')]
        try:
            self.formula = AllChem.ReactionFromSmarts(smarts)
        except Exception:
            raise ValueError('invalid transform SMARTS')


if __name__ == '__main__':
    # An example reaction with single atom reactant.
    smi = 'CCCCCCC(=C=O)CC(N)C(=O)O.O>>CCCCCC[C@H](C[C@H](N)C(=O)O)C(=O)O'
    rxn = Reaction(smi)
    rxn.get_descriptors()
