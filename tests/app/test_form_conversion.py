import pandas as pd

from app.conversion import _convert_feature_to_item, _convert_form_to_item
from chopin.schemas.composer import ComposerConfigItem, ComposerConfigRecommendation


def test__convert_form_to_item():
    in_df = pd.DataFrame().from_dict({"name": {"0": "pop", "1": "chill"}, "weight": {"0": 1, "1": 2}})
    out_item = _convert_form_to_item(in_df)
    assert isinstance(out_item, list)
    assert isinstance(out_item[0], ComposerConfigItem)
    assert out_item[0].name == "pop"
    assert out_item[0].weight == 1
    assert out_item[1].name == "chill"
    assert out_item[1].weight == 2


def test__convert_feature_to_item():
    in_df = pd.DataFrame().from_dict(
        {
            "name": {"0": "acousticness", "1": "instrumentalness"},
            "weight": {"0": 1, "1": 2},
            "value": {"0": 0.3, "1": 0.6},
        }
    )
    out_item = _convert_feature_to_item(in_df)
    assert isinstance(out_item, list)
    assert isinstance(out_item[0], ComposerConfigRecommendation)
    assert out_item[0].name == "acousticness"
    assert out_item[0].weight == 1
    assert out_item[0].value == 0.3
    assert out_item[1].name == "instrumentalness"
    assert out_item[1].value == 0.6
