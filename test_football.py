from football import world, universe, forecaster
import pdb
from numpy import random

def test_ham():
    # make universe, forecasters
    uu = universe(crowd={"pmm":1, "pmp":1, "truth":1}, p_t=0.55)
    wo = 14
    ga = 20
    uu.play(numworlds=wo, numgames=ga)
    assert 'brier_2' in uu.worlds[1].widedf.columns
    assert len(uu.worlds) == wo
    assert len(uu.worlds[3].widedf['brier_2']) == ga
    #pdb.set_trace()
    uu.plot_rank_freq()
    #pdb.set_trace()

def test_dist():
    uu = universe(crowd={"pmm":5,"truth":1}, d_t=random.uniform, low=0.2, high=0.8)
    uu.play(5,5)
    for w in uu.worlds:
        assert 0 in w.longdf.forecaster
        assert 0 in w.longdf.game

def test_vec():
    uu = universe(crowd={"pmm":1,"truth":1}, v_t=[0.4,0.5,0.33,0.89])
    uu.play(5,5)
    for w in uu.worlds:
        assert 0 in w.longdf.forecaster
        assert 0 in w.longdf.game

def test_world():
    mycrowd = [forecaster('pmm'), forecaster('pmp'), forecaster('truth')]
    # bug where length of games not same as length of ranks...
    for x in range(10,510,20):
        W = world(numgames=x, p_t=0.95, crowd=mycrowd)
        #derf = W.play(mycrowd)
        assert 'ign_rank' in W.longdf.columns
        assert sum(W.longdf.ign_rank) > x