from football import world, universe, forecaster
import pdb
from numpy import random

def test_ham():
    # make universe, forecasters
    uu = universe(crowd={"oversure":1, "averse":1, "truth":1}, p_t=0.55)
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
    uu = universe(crowd={"oversure":5,"truth":1}, d_t=random.uniform, low=0.2, high=0.8)
    uu.play(5,5)
    for w in uu.worlds:
        assert 0 in w.longdf.forecaster
        assert 0 in w.longdf.game

def test_vec():
    uu = universe(crowd={"oversure":1,"truth":1}, v_t=[0.4,0.5,0.33,0.89])
    uu.play(5,5)
    for w in uu.worlds:
        assert 0 in w.longdf.forecaster
        assert 0 in w.longdf.game

def test_world():
    mycrowd = [forecaster('oversure'), forecaster('averse'), forecaster('truth')]
    # bug where length of games not same as length of ranks...
    for x in range(10,510,20):
        W = world(numgames=x, p_t=0.95, crowd=mycrowd)
        #derf = W.play(mycrowd)
        assert 'ign_rank' in W.longdf.columns
        assert sum(W.longdf.ign_rank) > x

def test_ign():
    c = forecaster('truth') # archetype doesn't matter right now
    assert c.ign(0.7) > c.ign(0.5)
    assert c.ign(0.3) > c.ign(0.1)
    #assert c.brier(0.7) > c.brier(0.5)
    #assert c.brier(0.3) > c.brier(0.1)

def test_outcomes():
    uu3 = universe(crowd={'side':1,'oversure':1,'truth':1}, p_t=0.8)
    uu3.play(2**5,2**5)
    U = uu3.worlds[5].longdf
    assert sum(U['outcomes'])/len(U['outcomes']) > 0.5 # should be around 0.8

# take combos (0,1) with first two draws; compare analytically to graph dots