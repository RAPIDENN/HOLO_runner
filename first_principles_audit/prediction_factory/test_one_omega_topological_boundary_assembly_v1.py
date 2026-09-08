"""Independent boundary assembly controls, without a spectral or BF-domain claim."""
from __future__ import annotations

import pytest
import sympy as sp

from . import verify_one_omega_topological_boundary_assembly_v1 as oracle


EXPECTED_FIELDS = (
    "n", "N1", "N2", "N3", "H11", "H12", "H13", "H22", "H23", "H33",
    "tau", "omega", "vphi1", "vphi2", "vphi3",
)
METRIC_FIELDS = EXPECTED_FIELDS[:10]


@pytest.fixture(scope="module")
def model():
    return oracle.derive_model()


def zero(expression):
    if isinstance(expression, sp.MatrixBase):
        return all(sp.cancel(value) == 0 for value in expression)
    return sp.cancel(expression) == 0


def unit(model, field):
    result = sp.zeros(len(EXPECTED_FIELDS), 1)
    result[model["index"][field]] = 1
    return result


def metric_from_amplitudes(amplitudes):
    # Covariant metric perturbation, with both symmetric off-diagonal entries.
    h = sp.zeros(4)
    h[0, 0] = -2 * amplitudes["n"]
    for i in range(1, 4):
        h[0, i] = h[i, 0] = amplitudes[f"N{i}"]
        for j in range(1, 4):
            h[i, j] = amplitudes[f"H{min(i, j)}{max(i, j)}"]
    return h


def diffeomorphism_vector(model, direction):
    w, q = model["context"]["w"], model["context"]["q"]
    eta = sp.diag(-1, 1, 1, 1)
    k_cov = sp.Matrix([-w, 0, 0, q])
    xi_up = sp.eye(4)[:, direction]
    xi_cov = eta * xi_up
    dh = sp.I * (k_cov * xi_cov.T + xi_cov * k_cov.T)
    result = sp.zeros(len(EXPECTED_FIELDS), 1)
    index = model["index"]
    result[index["n"]] = -dh[0, 0] / 2
    for i in range(1, 4):
        result[index[f"N{i}"]] = dh[0, i]
        for j in range(i, 4):
            result[index[f"H{i}{j}"]] = dh[i, j]
    # T=t+tau is a scalar under the same active diffeomorphism convention.
    result[index["tau"]] = xi_up[0]
    return result, dh


def test_candidate_has_fifteen_fields_and_a_real_unrestricted_lambda(model):
    assert tuple(model["field_order"]) == EXPECTED_FIELDS
    assert model["H_full"].shape == (15, 15)
    assert not any(name.startswith("pi") for name in model["field_order"])
    coupling = model["parameters"]["lambda_K"]
    assert coupling.is_real is True
    assert coupling.is_positive is not True
    assert model["scope"]["null_cone_projector_extension_certified"] is False
    assert model["scope"]["BF_block_eliminated"] is False


def test_cross_tensor_force_has_bilateral_normalization_and_no_wall_contact(model):
    p, ctx = model["parameters"], model["context"]
    e = unit(model, "H12")
    bulk_force = model["H_T"] * e
    assert zero(bulk_force + p["M5c"] * p["K_T"] * e / 2)
    expected = -p["M5c"] * p["K_T"] / 2 + p["Mb2"] * (
        ctx["w"]**2 - p["xi"] * ctx["q"]**2
    ) / 2
    assert zero(model["H_full"] * e - expected * e)
    assert zero(sp.diff((e.T * model["H_full"] * e)[0], p["K_v"]))


def test_rotated_plus_and_cross_have_equal_quadratic_response(model):
    amplitude = sp.Symbol("independent_shear", real=True)
    r = sp.sqrt(2) / 2
    rotation = sp.Matrix([[r, r, 0], [-r, r, 0], [0, 0, 1]])
    cross = sp.Matrix([[0, amplitude, 0], [amplitude, 0, 0], [0, 0, 0]])
    assert rotation.det() == 1
    assert rotation * cross * rotation.T == sp.diag(amplitude, -amplitude, 0)
    plus_vector = unit(model, "H11") - unit(model, "H22")
    cross_vector = unit(model, "H12")
    for key in ("H_T", "H_bulk", "H_full"):
        matrix = model[key]
        assert zero((plus_vector.T * matrix * plus_vector)[0]
                    - (cross_vector.T * matrix * cross_vector)[0])


@pytest.mark.parametrize("direction", range(4))
def test_four_independently_constructed_diffeomorphisms_are_null(model, direction):
    vector, dh = diffeomorphism_vector(model, direction)
    assert not zero(vector)
    assert zero(model["H_full"] * vector)
    assert zero(model["H_bulk"] * vector)
    projected = oracle.project_metric(dh, model["context"]["w"], model["context"]["q"])
    assert zero(projected["TT"])
    assert zero(projected["Z"])


def test_material_dtn_and_finite_robin_spring_have_literal_signs(model):
    p, index = model["parameters"], model["index"]
    w, q = model["context"]["w"], model["context"]["q"]
    kappa, y, Z5, momentum = (p[name] for name in ("kappa_hat", "y", "Z5", "p_material"))
    expected_material = sp.zeros(15)
    expected_robin = sp.zeros(15)
    for direction in range(1, 4):
        material = unit(model, f"vphi{direction}")
        expected_material -= 2 * Z5 * momentum * material * material.T
        residual_plus = material
        residual_minus = material
        if direction == 3:
            residual_plus = material - sp.I * y * q * unit(model, "n") + y * q * w * unit(model, "tau")
            residual_minus = material + sp.I * y * q * unit(model, "n") + y * q * w * unit(model, "tau")
        expected_robin -= kappa * residual_minus * residual_plus.T
    assert zero(model["H_material"] - expected_material)
    # Differentiation isolates the literal local spring from the foliation.
    actual_robin = kappa * model["H_local"].diff(kappa)
    assert zero(actual_robin - expected_robin)
    coupled = actual_robin + model["H_material"]
    n, phi = index["n"], index["vphi3"]
    lapse_schur = coupled[n, n] - coupled[n, phi] * coupled[phi, n] / coupled[phi, phi]
    expected_load = -2 * kappa * Z5 * momentum * y**2 * q**2 / (kappa + 2 * Z5 * momentum)
    assert zero(lapse_schur - expected_load)
    assert zero(lapse_schur.subs(kappa, 0))
    assert zero(coupled[index["vphi1"], index["vphi1"]] + kappa + 2 * Z5 * momentum)


def test_negative_lambda_changes_the_full_extrinsic_trace_square(model):
    p = model["parameters"]
    w, q = model["context"]["w"], model["context"]["q"]
    trace_vector = sum((unit(model, name) for name in ("H11", "H22", "H33")), sp.zeros(15, 1))
    Kplus = -sp.I * w * trace_vector / 2 - sp.I * q * unit(model, "N3") + q**2 * unit(model, "tau")
    Kminus = sp.I * w * trace_vector / 2 + sp.I * q * unit(model, "N3") + q**2 * unit(model, "tau")
    independent_r = sp.Symbol("independent_positive_r", positive=True)
    negative = model["H_local"].subs(p["lambda_K"], -independent_r)
    zero_lambda = model["H_local"].subs(p["lambda_K"], 0)
    assert zero(negative - zero_lambda - p["Mb2"] * independent_r * Kminus * Kplus.T)


def test_beta_is_counted_once_as_the_induced_omega_stabilizer(model):
    d = unit(model, "omega")
    beta = model["parameters"]["beta"]
    assert zero(model["H_full"].diff(beta) + d * d.T)
    assert zero(model["H_local"] * d)
    wrong_double_wall = model["H_full"] - beta * d * d.T
    assert not zero(wrong_double_wall.diff(beta) + d * d.T)


@pytest.fixture(scope="module")
def christoffel_fierz_pauli_hessian(model):
    """EH Gamma-Gamma density from linear Christoffels, independent of projectors.

    Opposite Fourier factors contribute (-i)*(+i)=1; the connection below
    therefore stores the real k-linear coefficient. Both symmetric metric
    entries are present in every contraction.
    """
    eta = sp.diag(-1, 1, 1, 1)
    w, q = model["context"]["w"], model["context"]["q"]
    k = (-w, 0, 0, q)
    h = metric_from_amplitudes(model["amplitudes"])
    Gamma = {}
    for upper in range(4):
        for lower1 in range(4):
            for lower2 in range(4):
                Gamma[upper, lower1, lower2] = eta[upper, upper] * (
                    k[lower1] * h[upper, lower2]
                    + k[lower2] * h[upper, lower1]
                    - k[upper] * h[lower1, lower2]
                ) / 2
    density = 0
    for mu in range(4):
        for rho in range(4):
            for sigma in range(4):
                density += eta[mu, mu] * (
                    Gamma[rho, mu, sigma] * Gamma[sigma, mu, rho]
                    - Gamma[rho, mu, mu] * Gamma[sigma, rho, sigma]
                )
    density = sp.expand(model["parameters"]["M4_bulk_squared"] * density / 2)
    metric_amplitudes = tuple(model["amplitudes"][name] for name in METRIC_FIELDS)
    return sp.hessian(density, metric_amplitudes)


def test_all_one_hundred_ir_metric_entries_match_independent_christoffels(model, christoffel_fierz_pauli_hessian):
    indices = [model["index"][name] for name in METRIC_FIELDS]
    actual = model["H_IR"].extract(indices, indices)
    independent = christoffel_fierz_pauli_hessian
    assert actual.shape == independent.shape == (10, 10)
    residuals = [sp.cancel(actual[i, j] - independent[i, j]) for i in range(10) for j in range(10)]
    assert len(residuals) == 100
    assert all(value == 0 for value in residuals)
    assert zero(model["H_Fierz_Pauli"].extract(indices, indices) - independent)
    # These sectors vanish on a pure conformal trace-only probe.
    assert independent[METRIC_FIELDS.index("N1"), METRIC_FIELDS.index("H13")] != 0
    assert independent[METRIC_FIELDS.index("n"), METRIC_FIELDS.index("H11")] != 0


@pytest.mark.parametrize("row,column", [("N1", "H13"), ("n", "H11")])
def test_ir_vector_and_scalar_contaminations_fail_full_matrix_contrast(model, christoffel_fierz_pauli_hessian, row, column):
    indices = [model["index"][name] for name in METRIC_FIELDS]
    mutant = model["H_IR"].extract(indices, indices)
    i, j = METRIC_FIELDS.index(row), METRIC_FIELDS.index(column)
    mutant[i, j] += 1
    mutant[j, i] += 1
    assert not zero(mutant - christoffel_fierz_pauli_hessian)
    direction = 1 if row == "N1" else 0
    gauge, _ = diffeomorphism_vector(model, direction)
    metric_gauge = gauge.extract(indices, [0])
    assert not zero(mutant * metric_gauge)


@pytest.mark.parametrize("kind", ["second_wall", "old_solid"])
def test_added_wall_or_solid_contact_spoils_the_tt_response(model, kind):
    p, ctx = model["parameters"], model["context"]
    i = model["index"]["H12"]
    W0 = 3 * p["M5c"] * p["k_inf"] * sp.exp(-p["G"] / (6 * p["M5c"]))
    contact = 2 * W0 if kind == "second_wall" else -p["mu_X"] * p["v"]**4
    expected = -p["M5c"] * p["K_T"] / 2 + p["Mb2"] * (ctx["w"]**2 - p["xi"] * ctx["q"]**2) / 2
    mutant = model["H_full"][i, i] + contact
    assert zero(mutant - expected - contact)
    assert not zero(mutant - expected)
    # Only the already regular isolated TT entry is specialized; the full
    # Lorentz projector remains restricted to non-null slice momentum.
    assert zero(model["H_full"][i, i].subs({p["K_T"]: 0, p["xi"]: 1, ctx["w"]: ctx["q"]}))
    assert not zero(mutant.subs({p["K_T"]: 0, p["xi"]: 1, ctx["w"]: ctx["q"]}))


def test_resigned_receipt_cannot_change_an_assembled_tensor_entry():
    import copy
    import pytest
    from . import verify_one_omega_topological_boundary_assembly_v1 as oracle
    document=oracle.build_payload()
    assert document['source_comparison']['symbolic_entries_compared'] == 324
    mutant=copy.deepcopy(document)
    mutant['model']['H_full'][5][5]='999'
    mutant['calculation_digest']=oracle.canonical_digest({k:v for k,v in mutant.items() if k!='calculation_digest'})
    with pytest.raises(ValueError,match='fresh derivation'):
        oracle.validate_payload(mutant)
