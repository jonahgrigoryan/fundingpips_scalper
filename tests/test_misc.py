import src.inject_params as ip
import src.run_self_loop as rsl

def test_stub_mains(capsys):
    ip.main()
    rsl.main()
    captured = capsys.readouterr()
    assert "Not implemented" in captured.out