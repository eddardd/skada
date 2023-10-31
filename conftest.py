import numpy as np
import pytest
from skada.datasets import DomainAwareDataset, make_shifted_blobs


# xxx(okachaiev): old API has to be gone when re-writing is done
@pytest.fixture(scope="session")
def tmp_da_dataset():
    centers = np.array(
        [
            [0, 0],
            [1, 1],
        ]
    )
    _, n_features = centers.shape

    X, y, sample_domain = make_shifted_blobs(
        n_samples=100,
        centers=centers,
        n_features=n_features,
        shift=0.13,
        random_state=42,
        cluster_std=0.05,
        return_X_y=True,
    )

    return (
        X[sample_domain > 0], y[sample_domain > 0],
        X[sample_domain < 0], y[sample_domain < 0],
    )


@pytest.fixture(scope='session')
def da_dataset() -> DomainAwareDataset:
    centers = np.array([[0, 0], [1, 1]])
    _, n_features = centers.shape
    return make_shifted_blobs(
        n_samples=100,
        centers=centers,
        n_features=n_features,
        shift=0.13,
        random_state=42,
        cluster_std=0.05,
        return_dataset=True,
    )


@pytest.fixture(scope="session")
def tmp_folder(tmpdir_factory):
    folder = tmpdir_factory.mktemp("skada_datasets")
    return str(folder)
