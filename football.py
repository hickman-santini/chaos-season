"""
Example usage:
>>> uu = universe(crowd={"oversure":5,"truth":1}, d_t=random.uniform, low=0.2, high=0.8)
>>> uu.play(numgames=512, numworlds=1024)
"""
from typing import DefaultDict
from numpy import random, log2, nan
import pandas as pd
import pdb
import re

INSIDE_MARGIN = .10
NUM_GAMES = 2**10
NUM_WORLDS = 2**11
COLOR1 = 'c'
COLOR2 = 'r'
COLOR3 = 'g'

class forecaster:
    def __init__(self, archetype, *args):
        self.archetype = archetype
        if archetype not in ["oversure", "averse", "inside", "side", "truth"]:
            raise ValueError(f"{archetype} is not a valid archetype")
        if archetype == "inside":
            self.offset = random.uniform(-1*INSIDE_MARGIN,INSIDE_MARGIN)
        elif archetype == "averse":
            self.beta = random.uniform(0,1)
        elif archetype == "oversure":
            self.beta = random.uniform(0,1)
        elif archetype == "side":
            self.offset = random.uniform(0,.5)
        #elif archetype == "pmp":
        #    self.offset = 0.1
        #elif archetype == "pmm":
        #    self.offset = -0.1
        elif archetype == "truth": # P_T
            self.offset = 0
        self.allin = random.uniform(0,1)
        # How to hold their stats? Make a stats object that extends pd.DataFrame?

    def forecasts(self, p_t):
        p = []
        if self.archetype == 'oversure':
            for truth in p_t:
                if truth > 50:
                    p.append(1 - self.beta*(1-truth))
                else:
                    p.append(self.beta*truth)
        elif self.archetype == 'averse':
            for truth in p_t:
                p.append(0.5 + self.beta*(truth-0.5))
        elif self.archetype == 'side':
            for truth in p_t:
                if truth > 50:
                    p.append(0.5+self.offset)
                else:
                    p.append(0.5-self.offset)
        elif self.archetype == 'inside':
            for truth in p_t:
                p.append(truth + self.offset)
        elif self.archetype == 'truth':
            for truth in p_t:
                p.append(truth)
        else:
            raise ValueError('Oops! Don\'t have that archetype')
        self.preds = p
        return p
    
    def score(self, outcomes):
        self.igns = pd.Series([self.ign(p) if o == 1 else self.ign(1-p) for (o,p) in zip(outcomes, self.preds)])
        self.igns_cumsum = self.igns.cumsum()
        self.briers = pd.Series([self.brier(p) if o == 1 else self.brier(1-p) for (o,p) in zip(outcomes, self.preds)])
        self.briers_cumsum = self.briers.cumsum()

    def ign(self, p):
        # p is prob assigned to the correct outcome
        return 25 * (1 + log2(p)) #-log2(p)

    def brier(self, p):
        # p is prob assigned to the correct outcome
        return (1-p)**2

    def setid(self, id):
        self.id = id

    def __str__(self):
        return self.archetype
        

class universe:
    def __init__(self, crowd, p_t=None, d_t=None, v_t=None, str1="", **kwargs):
        self.p_t = p_t
        self.d_t = d_t
        self.v_t = v_t
        self.crowdsrc = crowd
        self.crowd = []
        self.strr = str1
        self.kwargs = kwargs
        for archetype, num in crowd.items():
            for i in range(num):
                self.crowd.append(forecaster(archetype))
        self.worlds = []
        self.time_to_99 = {'ign':[], 'brier':[]}

    def play(self, numworlds=NUM_WORLDS, numgames=NUM_GAMES):
        for w in range(numworlds):
            W = world(numgames, self.crowd, p_t=self.p_t, d_t=self.d_t, v_t=self.v_t, **self.kwargs)
            self.worlds.append(W)

    def plot_rank_freq(self, score='ign'):
        # assumes truth is last forecaster, sorry
        Q = pd.DataFrame([w.longdf[w.longdf['archetype'] == 'truth'][f'{score}_rank'] for w in self.worlds])
        freqs = Q.apply(lambda x: x.value_counts(normalize=True)).T
        freqs.columns = [name * 1.0 for name in freqs.columns]
        freqs = freqs.replace(nan, 0)[freqs.columns.intersection([1.0,2.0,3.0])]
        freqs = freqs.reset_index().drop('index', axis=1) # games
        for index, row in freqs.iterrows():
            if row[1.0] > 0.99:
                xmax = index
                break
        title = f'Truth: {self.strr}, Crowd: {str(self.crowdsrc)}, Score: {score}'
        if 'xmax' in locals():
            ax = freqs.plot(style={1.0:COLOR1, 2.0:COLOR2, 3.0:COLOR3}, kind='area', xlim=(0,xmax), title=title)
            self.time_to_99[score].append(xmax)
        else:
            ax = freqs.plot(style={1.0:COLOR1, 2.0:COLOR2, 3.0:COLOR3}, kind='area', title=title)
            self.time_to_99[score].append(None)
        ax.set_xlabel('# games')
        ax.set_ylabel('% worlds where truth is ranked...')

    def plot_rank_score(self, score='ign'):
        # IGN points after game vs rank before the game
        return 0


class world:
    def __init__(self, numgames, crowd, p_t=None, d_t=None, v_t=None, **kwargs):
        self.numgames = numgames
        self.upset = random.uniform(0,1)
        self.p_t = p_t
        self.d_t = d_t
        self.v_t = v_t
        self.truth = self.get_truth_vec(**kwargs)
        self.outcomes = self.get_outcomes()
        self.play(crowd)

    def get_truth_vec(self, **kwargs):
        """Given singular p_t or a distribution for truth, return outcome vector."""
        if self.v_t is not None:
            return self.v_t
        elif self.p_t is not None:
            return [self.p_t] * self.numgames
        elif self.d_t is not None:
            if 'loc' in kwargs: # normal
                return self.d_t(kwargs['loc'], kwargs['scale'], size=self.numgames)
            elif 'low' in kwargs: # uniform
                return self.d_t(kwargs['low'], kwargs['high'], size=self.numgames)
            elif 'left' in kwargs: # triangular
                return self.d_t(kwargs['left'], kwargs['mode'], kwargs['right'], size=self.numgames)
            else:
                raise ValueError(f"We haven\'t added that distribution yet, sorry")
        else:
            raise ValueError(f"Need to define p_t (single probability), v_t (vector), or d_t (distribution)")

    def get_outcomes(self):
        randos = [random.uniform(0,1) for x in range(self.numgames)]
        return [1 if t > r else 0 for r,t in zip(randos, self.truth)]

    def play(self, crowd):
        # Make the dataframe that we'll use to make the beautiful plots...
        self.widedf = pd.DataFrame(list(zip(range(self.numgames), self.outcomes, self.truth)), columns=['game', 'outcomes', 'truth'])
        # Forecasts and scores for each forecaster
        self.truths_ranks = {'ign': [], 'brier': []}
        for (caster, i) in zip(crowd, range(len(crowd))):
            caster.setid(i)
            self.widedf[f'p_{i}'] = caster.forecasts(self.truth)
            caster.score(self.outcomes) # CUMULATIVE MUST CHANGE
            self.widedf[f'ign_{i}'] = caster.igns_cumsum
            self.widedf[f'brier_{i}'] = caster.briers_cumsum
        # Ranks
        self.longdf = pd.wide_to_long(self.widedf, stubnames=['p_', 'ign_', 'brier_'], i='game', j='forecaster')           
        self.longdf['ign_rank'] = self.longdf.groupby('game')['ign_'].rank('dense', ascending=False)
        self.longdf['brier_rank'] = self.longdf.groupby('game')['brier_'].rank('dense', ascending=True)
        self.longdf = self.longdf.reset_index()
        self.longdf['archetype'] = self.longdf['forecaster'].apply(lambda x: crowd[x].archetype)
