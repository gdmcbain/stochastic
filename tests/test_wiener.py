import pychastic.vectorized_I_generation
import pychastic.wiener_integral_moments

import jax  # for PRNGKey generation
import jax.numpy as jnp
import numpy as np
import itertools


def test_integral_generation_euler():
    tested_scheme = "euler"

    # Prepare values of means and second moments = E(XY)
    tested_integrals = [[1], [2], [0]]  # [dW1,dW2,dt]
    tested_labels = ["d_w1", "d_w2", "d_t"]
    target_means = jnp.array(
        [pychastic.wiener_integral_moments.E(idx)(1) for idx in tested_integrals]
    )
    target_mean_products = jnp.array(
        [
            pychastic.wiener_integral_moments.E2(idx, idy)(1)
            for (idx, idy) in itertools.product(tested_integrals, tested_integrals)
        ]
    )

    samples_exponent = 14
    z_score_cutoff = 5

    seed = 0
    key = jax.random.PRNGKey(seed)
    sample_integrals = pychastic.vectorized_I_generation.get_wiener_integrals(
        key, scheme=tested_scheme, steps=2 ** samples_exponent, noise_terms=2
    )

    sample_integrals = jnp.array(
        [
            sample_integrals["d_w"][:, 0],
            sample_integrals["d_w"][:, 1],
            jnp.ones_like(sample_integrals["d_w"][:, 0]),
        ]
    ).T

    sample_means = jnp.mean(sample_integrals, axis=0)
    sample_mean_products = jnp.array(
        [
            jnp.mean(x * y)
            for (x, y) in itertools.product(sample_integrals.T, sample_integrals.T)
        ]
    )

    means_close = jnp.isclose(
        sample_means, target_means, atol=z_score_cutoff * 2 ** (-samples_exponent / 2)
    )
    means_error = sample_means - target_means
    assert means_close.all(), "Expected values incorrect \n" + str(
        {
            label: (bool(flag), float(error))
            for (flag, error, label) in zip(means_close, means_error, tested_labels)
        }
    )

    products_close = jnp.isclose(
        sample_mean_products,
        target_mean_products,
        atol=z_score_cutoff * 2 ** (-samples_exponent / 2),
    )
    products_error = sample_mean_products - target_mean_products
    assert products_close.all(), "Expected products incorrect \n" + str(
        {
            label: (bool(flag), float(error))
            for (flag, error, label) in zip(
                products_close,
                products_error,
                itertools.product(tested_labels, tested_labels),
            )
        }
    )
    
    
    
    
def test_integral_generation_milstein():
    tested_scheme = "milstein"

    # Prepare values of means and second moments = E(XY)
    tested_integrals = [[1,1], [1,2], [2,1], [2,2], [1], [2], [0]]  # [dW1,dW2,dt]
    tested_labels = ["d_w1 d_w1", "d_w1 d_w2", "d_w2 d_w1", "d_w2 d_w2", "d_w1", "d_w2", "d_t"]
    target_means = jnp.array(
        [pychastic.wiener_integral_moments.E(idx)(1) for idx in tested_integrals]
    )
    target_mean_products = jnp.array(
        [
            pychastic.wiener_integral_moments.E2(idx, idy)(1)
            for (idx, idy) in itertools.product(tested_integrals, tested_integrals)
        ]
    )

    samples_exponent = 14
    z_score_cutoff = 5

    seed = 0
    key = jax.random.PRNGKey(seed)
    sample_integrals = pychastic.vectorized_I_generation.get_wiener_integrals(
        key, scheme=tested_scheme, steps=2 ** samples_exponent, noise_terms=2
    )

    sample_integrals = jnp.array(
        [
            sample_integrals["d_ww"][:,0,0],
            sample_integrals["d_ww"][:,0,1],
            sample_integrals["d_ww"][:,1,0],
            sample_integrals["d_ww"][:,1,1],
            sample_integrals["d_w"][:, 0],
            sample_integrals["d_w"][:, 1],
            jnp.ones_like(sample_integrals["d_w"][:, 0]),
        ]
    ).T

    sample_means = jnp.mean(sample_integrals, axis=0)
    sample_mean_products = jnp.array(
        [
            jnp.mean(x * y)
            for (x, y) in itertools.product(sample_integrals.T, sample_integrals.T)
        ]
    )

    means_close = jnp.isclose(
        sample_means, target_means, atol=z_score_cutoff * 2 ** (-samples_exponent / 2)
    )
    means_error = sample_means - target_means
    assert means_close.all(), "Expected values incorrect \n" + str(
        {
            label: (bool(flag), float(error))
            for (flag, error, label) in zip(means_close, means_error, tested_labels)
        }
    )

    products_close = jnp.isclose(
        sample_mean_products,
        target_mean_products,
        atol=z_score_cutoff * 2 ** (-samples_exponent / 2),
    )
    products_error = sample_mean_products - target_mean_products
    assert products_close.all(), "Expected products incorrect \n" + str(
        {
            label: (bool(flag), float(error))
            for (flag, error, label) in zip(
                products_close,
                products_error,
                itertools.product(tested_labels, tested_labels),
            )
        }
    )

def test_integral_generation_wagner_platen_1d():
    tested_scheme = "wagner_platen"

    # Prepare values of means and second moments = E(XY)
    tested_integrals = [[1,1,1], [1,0], [0,1] , [1,1], [1], [0]]  # [dW1,dW2,dt]
    tested_labels = ["d_www","d_wt","d_tw","d_ww","d_w","d_t"]
    target_means = jnp.array(
        [pychastic.wiener_integral_moments.E(idx)(1) for idx in tested_integrals]
    )
    target_mean_products = jnp.array(
        [
            pychastic.wiener_integral_moments.E2(idx, idy)(1)
            for (idx, idy) in itertools.product(tested_integrals, tested_integrals)
        ]
    )

    samples_exponent = 14
    z_score_cutoff = 5

    seed = 0
    key = jax.random.PRNGKey(seed)
    sample_integrals = pychastic.vectorized_I_generation.get_wiener_integrals(
        key, scheme=tested_scheme, steps=2 ** samples_exponent, noise_terms=1
    )

    sample_integrals = jnp.array(
        [
            sample_integrals["d_www"][:,0,0,0],
            sample_integrals["d_wt"][:,0,0],
            sample_integrals["d_tw"][:,0,0],
            sample_integrals["d_ww"][:,0,0],
            sample_integrals["d_w"][:, 0],
            jnp.ones_like(sample_integrals["d_w"][:, 0]),
        ]
    ).T

    sample_means = jnp.mean(sample_integrals, axis=0)
    sample_mean_products = jnp.array(
        [
            jnp.mean(x * y)
            for (x, y) in itertools.product(sample_integrals.T, sample_integrals.T)
        ]
    )

    means_close = jnp.isclose(
        sample_means, target_means, atol=z_score_cutoff * 2 ** (-samples_exponent / 2)
    )
    means_error = sample_means - target_means
    assert means_close.all(), "Expected values incorrect \n" + str(
        {
            label: (bool(flag), float(error))
            for (flag, error, label) in zip(means_close, means_error, tested_labels)
        }
    )

    products_close = jnp.isclose(
        sample_mean_products,
        target_mean_products,
        atol=z_score_cutoff * 2 ** (-samples_exponent / 2),
    )
    products_error = sample_mean_products - target_mean_products
    assert products_close.all(), "Expected products incorrect \n" + str(
        {
            label: (bool(flag), float(error))
            for (flag, error, label) in zip(
                products_close,
                products_error,
                itertools.product(tested_labels, tested_labels),
            )
        }
    )

if __name__ == "__main__":
    test_integral_generation_euler()
    test_integral_generation_wagner_platen_1d()


#     tested_integrals = [[1],[2],[0],[1,1],[1,2],[1,0],[2,0],[0,1],[0,2],[1,1,1]]
