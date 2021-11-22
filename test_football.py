from football import world, universe, forecaster
import pdb

def test_ham():
    # make universe, forecasters
    uu = universe(p_t=0.55, **{"pmm":1, "pmp":1, "truth":1})
    wo = 14
    ga = 20
    uu.play(numworlds=wo, numgames=ga)
    assert 'brier_2' in uu.worlds[1].bigdf.columns
    assert len(uu.worlds) == wo
    assert len(uu.worlds[3].bigdf['brier_2']) == ga
    pdb.set_trace()
    uu.plot_rank_freq()
    #pdb.set_trace()

def test_world():
    mycrowd = [forecaster('pmm'), forecaster('pmp'), forecaster('truth')]
    W = world(numgames=10, p_t=0.95, crowd=mycrowd)
    #derf = W.play(mycrowd)
    assert len(W.truths_ranks['ign']) == 10
    assert len(W.truths_ranks['brier']) == 10
