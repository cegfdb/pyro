# Copyright Contributors to the Pyro project.
# SPDX-License-Identifier: Apache-2.0

import pytest
import torch

from pyro.contrib.outbreak import SIRModel


@pytest.mark.parametrize("duration", [3, 7])
@pytest.mark.parametrize("forecast", [0, 7])
def test_smoke(duration, forecast):
    population = 100
    recovery_time = 7.0

    # Generate data.
    model = SIRModel(population, recovery_time, [None] * duration)
    for attempt in range(100):
        samples = model.generate({"R0": 1.5, "rho": 0.5})
        data = torch.stack([v for k, v in samples.items() if k.startswith("obs_")])
        if data.sum():
            break
    assert data.sum() > 0, "failed to generate positive data"

    # Infer.
    model = SIRModel(population, recovery_time, data)
    model.fit(warmup_steps=2, num_samples=5, max_tree_depth=2)

    # Predict and forecast.
    model.predict(forecast=forecast)
