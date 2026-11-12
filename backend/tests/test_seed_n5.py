from app.seed_n5 import EXPECTED_N5_COUNT, load_n5_rows


def test_n5_dataset_is_complete_and_valid():
    rows = load_n5_rows()

    assert len(rows) == EXPECTED_N5_COUNT
    assert len({row["source_id"] for row in rows}) == EXPECTED_N5_COUNT
    assert len({(row["term"], row["reading"]) for row in rows}) == EXPECTED_N5_COUNT
    assert all(row["meaning_en"] and row["meaning_vi"] for row in rows)
