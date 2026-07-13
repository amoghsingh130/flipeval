from scripts.compare_mmlu_reference import _reference_row, _score


def test_score_accepts_nested_lm_eval_response_shape():
    assert _score([[[-1.25, False]]]) == -1.25


def test_reference_row_maps_task_and_doc_id_to_pilot_identity():
    sample = {
        "task_name": "mmlu_abstract_algebra",
        "doc_id": 7,
        "doc": {"answer": 1},
        "resps": [[[-4.0, False]], [[-0.2, True]], [[-2.0, False]], [[-3.0, False]]],
    }
    assert _reference_row(sample) == ("abstract_algebra:test:7", "B", "B", True)
