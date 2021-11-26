"""

"""
from numpy import random, log2, nan
import pandas as pd
import pdb
import re

INSIDE_MARGIN = .10
NUM_GAMES = 1024
NUM_WORLDS = 512

class forecaster:
    def __init__(self, archetype, *args):
        self.archetype = archetype
        if archetype not in ["oversure", "averse", "inside", "side", "pmp", "pmm", "truth"]:
            raise ValueError(f"{archetype} is not a valid archetype")
        if archetype == "inside":
            self.offset = random.uniform(-1*INSIDE_MARGIN,INSIDE_MARGIN)
        elif archetype == "averse":
            self.beta = random.uniform(0,1)
        elif archetype == "side":
            self.offset = random.uniform(0,.5)
        elif archetype == "pmp":
            self.offset = 0.01
        elif archetype == "pmm":
            self.offset = -0.01
        elif archetype == "truth": # P_T
            self.offset = 0
        self.allin = random.uniform(0,1)
        # How to hold their stats? Make a stats object that extends pd.DataFrame?

    def forecasts(self, p_t):
        p = []
        for truth in p_t:
            p.append(truth + self.offset)
        self.preds = p
        return p
    
    def score(self, outcomes):
        self.igns = pd.Series([self.ign(p) if o == 1 else self.ign(1-p) for (o,p) in zip(outcomes, self.preds)])
        self.igns_cumsum = self.igns.cumsum()
        self.briers = pd.Series([self.brier(p) if o == 1 else self.brier(1-p) for (o,p) in zip(outcomes, self.preds)])
        self.briers_cumsum = self.briers.cumsum()

    def ign(self, p):
        # p is prob assigned to the correct outcome
        #pdb.set_trace()
        return 25 * 1 + log2(p)

    def brier(self, p):
        # p is prob assigned to the correct outcome
        return (1-p)**2
        

class universe:
    def __init__(self, p_t, **kwargs):
        self.p_t = p_t # temporary - constant p_t
        self.crowd = [] 
        for archetype, num in kwargs.items():
            for i in range(num):
                self.crowd.append(forecaster(archetype))
        self.worlds = []

    def play(self, numworlds=NUM_WORLDS, numgames=NUM_GAMES):
        for w in range(numworlds):
            W = world(numgames, self.p_t, self.crowd)
            self.worlds.append(W)

    def plot_rank_freq(self):
        q = pd.DataFrame([w.truths_ranks['ign'] for w in self.worlds])
        freqs = q.apply(lambda x: x.value_counts(normalize=True)).T
        freqs.columns = [name * 1.0 for name in freqs.columns]
        freqs = freqs.replace(nan, 0)[freqs.columns.intersection([1.0,2.0,3.0])]
        freqs.plot(style={1.0:'b', 2.0:'r', 3.0:'g'})


class world:
    def __init__(self, numgames, p_t, crowd, **kwargs):
        self.numgames = numgames
        self.upset = random.uniform(0,1)
        self.p_t = p_t
        randos = [random.uniform(0,1) for x in range(self.numgames)]
        self.outcomes = [1 if x > self.p_t else 0 for x in randos]
        self.play(crowd)

    def play(self, crowd):
        # Make the dataframe that we'll use to make the beautiful plots...
        self.bigdf = pd.DataFrame(list(zip(self.outcomes, [self.p_t] * self.numgames)), columns=['outcomes', 'truth'])
        # Forecasts and scores for each forecaster
        self.truths_ranks = {'ign': [], 'brier': []}
        for (caster, i) in zip(crowd, range(len(crowd))):
            self.bigdf[f'p_{i}'] = caster.forecasts([self.p_t] * self.numgames)
            caster.score(self.outcomes) # CUMULATIVE MUST CHANGE
            self.bigdf[f'ign_{i}'] = caster.igns_cumsum
            self.bigdf[f'brier_{i}'] = caster.briers_cumsum
            # Truth's Ranks....just truth for now. Which is truth? oops... let's assume truth always last (not ideal)
            if caster.archetype == 'truth':
                self.get_truths_ranks_ign(self.bigdf, caster)
                self.get_truths_ranks_brier(self.bigdf, caster)

    def get_truths_ranks_ign(self, df, caster):
        cols = list(filter(lambda c: re.match(f'ign_*', c), df.columns))
        for index, row in df.iterrows():
            scores = [x for x in row[cols]] # ign
            #pdb.set_trace()
            scores.sort(reverse=True)
            for (y, score) in zip(range(len(scores)), scores):
                if score == caster.igns_cumsum[index]:
                    self.truths_ranks['ign'].append(y+1)
                    continue


    def get_truths_ranks_brier(self, df, caster):
        cols = list(filter(lambda c: re.match(f'brier_*', c), df.columns))
        for index, row in df.iterrows():
            scores = [x for x in row[cols]] # ign
            #pdb.set_trace()
            scores.sort(reverse=True)
            for (y, score) in zip(range(len(scores)), scores):
                if score == caster.briers_cumsum[index]:
                    self.truths_ranks['brier'].append(y+1)
                    continue