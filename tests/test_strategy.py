from fundingpips_scalper import strategy

def test_generate_signals():
    assert strategy.generate_signals() == []