from acta.micrograph import make_micrograph


def test_deterministic_and_data_present(tmp_path):
    a = make_micrograph("seed", "Aerospace", tmp_path / "a.png")
    b = make_micrograph("seed", "Aerospace", tmp_path / "b.png")
    assert a == b and (tmp_path / "a.png").read_bytes() == (tmp_path / "b.png").read_bytes()
    assert a["material"].startswith("Ti-6Al-4V") and a["mean_d_um"] > 0 and a["astm_g"] > 0


def test_unknown_domain_falls_back(tmp_path):
    assert make_micrograph("x", "Nonsense", tmp_path / "c.png")["mag"] == 200
