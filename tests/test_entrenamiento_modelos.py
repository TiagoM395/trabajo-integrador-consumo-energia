import tempfile
import unittest
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from entrenamiento_modelos import (
    FEATURES,
    META_KWH,
    build_dataset,
    chronological_split,
)


class TestEntrenamientoModelos(unittest.TestCase):
    def test_build_dataset_uses_future_energy_only_as_target(self):
        start = date(2007, 1, 1).toordinal() * 24
        index = pd.Index(range(start, start + 24 * 20), name="hour_id")
        active = np.arange(len(index), dtype=float) / 100 + 1
        hourly = pd.DataFrame(
            {
                "active": active,
                "reactive": np.full(len(index), 0.1),
                "voltage": np.full(len(index), 230.0),
                "sub1": np.full(len(index), 0.1),
                "sub2": np.full(len(index), 0.2),
                "sub3": np.full(len(index), 0.3),
            },
            index=index,
        )
        weather = pd.DataFrame(
            {
                "date": [
                    date.fromordinal(start // 24 + offset).isoformat()
                    for offset in range(20)
                ],
                "temp_mean": np.full(20, 12.0),
            }
        )

        with tempfile.TemporaryDirectory() as directory:
            weather_path = Path(directory) / "clima.csv"
            weather.to_csv(weather_path, index=False)
            samples, _ = build_dataset(hourly, weather_path)

        first = samples.iloc[0]
        position = int(first.name - start)
        self.assertEqual(list(samples[FEATURES].columns), FEATURES)
        self.assertAlmostEqual(first["kwh_h"], active[position])
        self.assertAlmostEqual(
            first["active_24"], active[position - 23 : position + 1].sum()
        )
        self.assertAlmostEqual(
            first["target_kwh_next24"], active[position + 1 : position + 25].sum()
        )
        self.assertEqual(
            first["target_exceso"],
            int(first["target_kwh_next24"] > META_KWH),
        )
        self.assertEqual(first["temp_actual"], first["temp_next24"])

    def test_chronological_split_purges_target_window_overlap(self):
        samples = pd.DataFrame(index=pd.Index(range(1000), name="hour_id"))
        splits = chronological_split(samples)
        train = splits["entrenamiento"]
        validation = splits["validación"]
        test = splits["prueba"]

        self.assertLess(train.index.max() + 24, validation.index.min())
        self.assertLess(validation.index.max() + 24, test.index.min())
        self.assertGreater(len(train), len(validation))
        self.assertGreater(len(validation), 0)
        self.assertGreater(len(test), 0)


if __name__ == "__main__":
    unittest.main()
