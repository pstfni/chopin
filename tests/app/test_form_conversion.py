import pandas as pd

from app.conversion import _convert_form_to_item
from chopin.schemas.composer import ComposerConfigItem


def test__convert_form_to_item():
    in_df = pd.DataFrame().from_dict({"name": {"0": "pop", "1": "chill"}, "weight": {"0": 1, "1": 2}})
    out_item = _convert_form_to_item(in_df)
    assert isinstance(out_item, list)
    assert isinstance(out_item[0], ComposerConfigItem)
    assert out_item[0].name == "pop"
    assert out_item[0].weight == 1
    assert out_item[1].name == "chill"
    assert out_item[1].weight == 2
