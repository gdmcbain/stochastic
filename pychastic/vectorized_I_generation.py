import jax.numpy as jnp
import jax


def fill_diagonal(mat, vec):
    (n, _) = mat.shape
    i, j = jnp.diag_indices(n)
    return mat.at[i, j].set(vec)

vectorized_fill_diagonal = jax.vmap(fill_diagonal, in_axes=(0, 0))


# Compare Kloden-Platen (10.3.7), dimension = d, noiseterms = m
# Generate 'steps' stochastic integral increments at once
def get_wiener_integrals(key, steps=1, noise_terms=1, scheme="euler", p=10):
    """
    Calculate moments of principal wiener integrals.

    Parameters
    ----------
    key : jax.PRNGKey
        source of randomness
    steps : int, optional
        number of steps
    noise_terms : int, optional
        wiener process dimension
    scheme : ('euler' or 'milstein' or 'wagner_platen')
        controls order of integrals generated and method of generation
    p : int, optional
        controls series truncation

    Returns
    -------
    dict
        Keys are like 'd_w' or 'd_wt' and values are `jnp.arrays`
    """
    if scheme == 'euler' or (scheme == 'milstein' and noise_terms == 1):
        dW_scaled = jax.random.normal(key, shape=(steps, noise_terms))

        if scheme == 'euler':
            return {
                'd_w' : dW_scaled
            }

        dI_scaled = 0.5*(dW_scaled**2 - 1)[..., jax.numpy.newaxis] # noise_terms == 1 is special

        if scheme == 'milstein':
            return {
                'd_w' : dW_scaled,
                'd_ww' : dI_scaled
            }
    elif scheme == 'milstein':
        key1, key2, key3, key4 = jax.random.split(key, num=4)
        xi = jax.random.normal(key1, shape=(steps, 1,noise_terms))
        dW_scaled = xi.squeeze() #jax.random.normal(key2, shape=(steps,noise_terms))

        mu = jax.random.normal(key2, shape=(steps, 1,noise_terms))

        eta = jax.random.normal(key3, shape=(steps, p,noise_terms))

        zeta = jax.random.normal(key4, shape=(steps, p,noise_terms))

        rec = 1 / jax.numpy.arange(1, p + 1)  # 1/r vector
        rho = 1 / 12 - (rec ** 2).sum() / (2 * jax.numpy.pi ** 2)

        a = jax.numpy.sqrt(2) * xi + eta

        Imat_nodiag = (
            xi * jax.numpy.transpose(xi, axes=(0, 2, 1)) / 2
            + jax.numpy.sqrt(rho)
            * (mu * jax.numpy.transpose(xi, axes=(0, 2, 1)) - xi * jax.numpy.transpose(mu, axes=(0, 2, 1)))
            + 1.0
            / (2 * jnp.pi)
            * (
                (
                    jnp.expand_dims(a, 2) * jnp.expand_dims(zeta, 3)
                    - jnp.expand_dims(a, 3) * jnp.expand_dims(zeta, 2)
                )
                * rec[:, jax.numpy.newaxis, jax.numpy.newaxis]
            ).sum(axis=1)
        )

        dI_scaled = vectorized_fill_diagonal(
            Imat_nodiag, 0.5 * (xi ** 2 - 1).squeeze()
        )  # Diagonal entries work differently

        return {
                'd_w': dW_scaled,
                'd_ww': dI_scaled
            }

    elif scheme == 'wagner_platen':
        if noise_terms == 1:
            u = jax.random.normal(key, shape=(2, steps, noise_terms))
            dW_scaled = u[0]
            dZ_scaled = 0.5*(u[0] + 3**(-0.5)*u[1])[..., jax.numpy.newaxis]

            dI_scaled = 0.5*(dW_scaled**2 - 1)[..., jax.numpy.newaxis]

            return {
                'd_w': dW_scaled,
                'd_ww': dI_scaled,
                'd_wt': dZ_scaled,
                'd_tw': dW_scaled[..., jax.numpy.newaxis] - dZ_scaled,
                'd_www': (0.5*((1.0/3.0)*dW_scaled**2-1)*dW_scaled)[..., jax.numpy.newaxis, jax.numpy.newaxis],
            }

        else:
            raise NotImplementedError

    else:
        raise NotImplementedError

if __name__ == '__main__':
    seed = 0
    key = jax.random.PRNGKey(seed)
    get_wiener_integrals(key, steps=3, noise_terms=1)
    get_wiener_integrals(key, steps=3, noise_terms=2)
