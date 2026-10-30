#!/usr/bin/env python3
"""Write a small synthetic rotation sweep as Pilatus miniCBF images.

This is a *regression fixture*, not a realistic simulation: its purpose is
to exercise the d*TREK command-line pipeline end to end, deterministically,
so that outputs can be compared byte-for-byte before and after a code
change.  It is not a substitute for testing on real data.

Recorded counts include the rotation Lorentz factor and the polarisation
factor for an unpolarised beam, so that symmetry-equivalent reflections
agree after correction.

Geometry follows the miniCBF convention d*TREK uses for Pilatus data:
rotation axis +X, beam travelling along -Z, detector normal to the beam at
Z = -distance, fast pixel axis +X, slow pixel axis -Y.

Only numpy is required.  Output is deterministic for a given --seed.
"""

import argparse
import base64
import hashlib
import os

import numpy as np

NX, NY = 2463, 2527  # Pilatus 6M
PIXEL = 0.172  # mm


def byte_offset(data):
    """CBF byte-offset compression of a flat int32 array."""
    values = data.astype(np.int64).ravel()
    delta = np.diff(np.concatenate(([0], values)))
    small = np.abs(delta) <= 127
    medium = ~small & (np.abs(delta) <= 32767)
    large = ~small & ~medium
    length = np.where(small, 1, np.where(medium, 3, 7))
    offset = np.concatenate(([0], np.cumsum(length)[:-1]))
    out = np.zeros(int(length.sum()), dtype=np.uint8)
    out[offset[small]] = (delta[small] & 0xFF).astype(np.uint8)
    m = offset[medium]
    d = delta[medium] & 0xFFFF
    out[m] = 0x80
    out[m + 1] = (d & 0xFF).astype(np.uint8)
    out[m + 2] = (d >> 8).astype(np.uint8)
    g = offset[large]
    d = delta[large] & 0xFFFFFFFF
    out[g] = 0x80
    out[g + 1] = 0x00
    out[g + 2] = 0x80
    for k in range(4):
        out[g + 3 + k] = ((d >> (8 * k)) & 0xFF).astype(np.uint8)
    return out.tobytes()


def write_minicbf(filename, image, phi, dphi, args):
    binary = byte_offset(image)
    md5 = base64.b64encode(hashlib.md5(binary).digest()).decode()
    header = "\n".join(
        [
            "# Detector: PILATUS 6M, S/N 60-0000",
            "# 2026-10-30T00:00:00.000",
            "# Pixel_size 172e-6 m x 172e-6 m",
            "# Silicon sensor, thickness 0.000450 m",
            "# Exposure_time 0.1000000 s",
            "# Exposure_period 0.1000000 s",
            "# Count_cutoff 1048574 counts",
            f"# Wavelength {args.wavelength:.5f} A",
            f"# Detector_distance {args.distance / 1000.0:.5f} m",
            f"# Beam_xy ({args.beam_x:.2f}, {args.beam_y:.2f}) pixels",
            f"# Start_angle {phi:.4f} deg.",
            f"# Angle_increment {dphi:.4f} deg.",
            "# Detector_2theta 0.0000 deg.",
            "# Polarization 0.500",
            "# Omega 0.0000 deg.",
            "# Kappa 0.0000 deg.",
            "# Phi 0.0000 deg.",
            "# Chi 0.0000 deg.",
        ]
    )
    text = (
        "###CBF: VERSION 1.5, synthetic d*TREK regression fixture\r\n\r\n"
        "data_" + os.path.basename(filename)[:-4] + "\r\n\r\n"
        "_array_data.header_convention \"PILATUS_1.2\"\r\n"
        "_array_data.header_contents\r\n;\r\n"
        + header.replace("\n", "\r\n")
        + "\r\n;\r\n\r\n"
        "_array_data.data\r\n;\r\n"
        "--CIF-BINARY-FORMAT-SECTION--\r\n"
        "Content-Type: application/octet-stream;\r\n"
        "     conversions=\"x-CBF_BYTE_OFFSET\"\r\n"
        "Content-Transfer-Encoding: BINARY\r\n"
        f"X-Binary-Size: {len(binary)}\r\n"
        "X-Binary-ID: 1\r\n"
        "X-Binary-Element-Type: \"signed 32-bit integer\"\r\n"
        "X-Binary-Element-Byte-Order: LITTLE_ENDIAN\r\n"
        f"Content-MD5: {md5}\r\n"
        f"X-Binary-Number-of-Elements: {NX * NY}\r\n"
        f"X-Binary-Size-Fastest-Dimension: {NX}\r\n"
        f"X-Binary-Size-Second-Dimension: {NY}\r\n"
        "X-Binary-Size-Padding: 4095\r\n\r\n"
    )
    with open(filename, "wb") as f:
        f.write(text.encode("ascii"))
        f.write(b"\x0c\x1a\x04\xd5")
        f.write(binary)
        f.write(b"\x00" * 4095)
        f.write(b"\r\n--CIF-BINARY-FORMAT-SECTION----\r\n;\r\n\r\n")


def b_matrix(a, b, c):
    """B matrix for a tetragonal / orthorhombic cell (alpha=beta=gamma=90)."""
    return np.diag([1.0 / a, 1.0 / b, 1.0 / c])


def random_rotation(rng):
    q = rng.normal(size=4)
    q /= np.linalg.norm(q)
    w, x, y, z = q
    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ]
    )


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("directory")
    p.add_argument("--images", type=int, default=30)
    p.add_argument("--osc", type=float, default=0.5, help="degrees per image")
    p.add_argument("--wavelength", type=float, default=0.9795)
    p.add_argument("--distance", type=float, default=200.0, help="mm")
    p.add_argument("--beam-x", type=float, default=1231.5, help="pixels (fast)")
    p.add_argument("--beam-y", type=float, default=1263.5, help="pixels (slow)")
    p.add_argument("--dmin", type=float, default=1.8)
    p.add_argument("--mosaic", type=float, default=0.15, help="sigma, degrees")
    p.add_argument("--spot-sigma", type=float, default=1.2, help="pixels")
    p.add_argument("--background", type=float, default=8.0)
    p.add_argument("--seed", type=int, default=20261030)
    args = p.parse_args()

    rng = np.random.default_rng(args.seed)
    os.makedirs(args.directory, exist_ok=True)

    # Lysozyme-like P4(3)2(1)2 cell
    a, c = 79.1, 37.9
    UB = random_rotation(rng) @ b_matrix(a, a, c)
    hmax = int(a / args.dmin) + 1
    lmax = int(c / args.dmin) + 1
    h, k, l = np.mgrid[-hmax : hmax + 1, -hmax : hmax + 1, -lmax : lmax + 1]
    hkl = np.stack([h.ravel(), k.ravel(), l.ravel()], axis=1)
    hkl = hkl[np.any(hkl != 0, axis=1)]
    r = hkl @ UB.T
    r2 = (r * r).sum(axis=1)
    keep = r2 <= 1.0 / args.dmin**2
    # systematic absences for P4(3)2(1)2
    hh, kk, ll = hkl[:, 0], hkl[:, 1], hkl[:, 2]
    absent = ((hh == 0) & (kk == 0) & (ll % 4 != 0)) | (
        (kk == 0) & (ll == 0) & (hh % 2 != 0)
    ) | ((hh == 0) & (ll == 0) & (kk % 2 != 0))
    keep &= ~absent
    hkl, r, r2 = hkl[keep], r[keep], r2[keep]

    # Wilson intensities, identical for symmetry mates under 422 + Friedel
    key = np.stack(
        [
            np.maximum(np.abs(hkl[:, 0]), np.abs(hkl[:, 1])),
            np.minimum(np.abs(hkl[:, 0]), np.abs(hkl[:, 1])),
            np.abs(hkl[:, 2]),
        ],
        axis=1,
    )
    unique, inverse = np.unique(key, axis=0, return_inverse=True)
    inverse = inverse.ravel()
    intensity = rng.exponential(1.0, size=len(unique))[inverse]
    intensity *= 20000.0 * np.exp(-2.0 * 20.0 * r2 / 4.0)

    # Rotation about +X: s = s0 + R(phi) r, s0 = (0, 0, -1/lambda)
    lam = args.wavelength
    A, B = r[:, 1], r[:, 2]
    C = lam * r2 / 2.0
    rho = np.hypot(A, B)
    ok = np.abs(C) < rho
    base = np.arctan2(A, B)
    obs = []
    for sign in (+1, -1):
        alpha = np.arccos(np.clip(C / np.where(ok, rho, 1.0), -1, 1))
        phi = (base + sign * alpha) % (2 * np.pi)
        cphi, sphi = np.cos(phi), np.sin(phi)
        rx = r[:, 0]
        ry = A * cphi - B * sphi
        rz = A * sphi + B * cphi
        sx, sy, sz = rx, ry, rz - 1.0 / lam
        good = ok & (sz < 0)
        t = -args.distance / np.where(good, sz, -1.0)
        fx = args.beam_x + t * sx / PIXEL
        fy = args.beam_y - t * sy / PIXEL
        good &= (fx > 5) & (fx < NX - 5) & (fy > 5) & (fy < NY - 5)
        # Recorded counts are I / (Lorentz-polarisation correction): the
        # Lorentz term for rotation about X is |X . (s1 x s0)| / (|s1||s0|),
        # polarisation is for an unpolarised beam (header Polarization 0.5).
        inv_lam = 1.0 / lam
        cross_x = sy * (-inv_lam)  # (s1 x s0).x with s0 = (0, 0, -1/lambda)
        lorentz = np.abs(cross_x) / (inv_lam * inv_lam)
        cos2t = -sz * lam
        polar = 0.5 * (1.0 + cos2t * cos2t)
        good &= lorentz > 0.02
        counts = intensity * polar / np.where(lorentz > 0, lorentz, 1.0)
        obs.append(np.stack([np.degrees(phi), fx, fy, counts], axis=1)[good])
    obs = np.concatenate(obs)

    from math import erf, sqrt

    verf = np.vectorize(erf)
    win = np.arange(-4, 5)
    for i in range(args.images):
        phi0 = i * args.osc
        phi1 = phi0 + args.osc
        image = rng.poisson(args.background, size=(NY, NX)).astype(np.int32)
        z0 = (phi0 - obs[:, 0]) / (args.mosaic * sqrt(2))
        z1 = (phi1 - obs[:, 0]) / (args.mosaic * sqrt(2))
        near = (z1 > -6) & (z0 < 6)
        frac = 0.5 * (verf(z1[near]) - verf(z0[near]))
        for (phi, fx, fy, inten), f in zip(obs[near], frac):
            mean = inten * f
            if mean < 0.5:
                continue
            cx, cy = int(round(fx)), int(round(fy))
            gx = np.exp(-0.5 * ((cx + win - fx) / args.spot_sigma) ** 2)
            gy = np.exp(-0.5 * ((cy + win - fy) / args.spot_sigma) ** 2)
            profile = np.outer(gy, gx)
            profile /= profile.sum()
            image[cy - 4 : cy + 5, cx - 4 : cx + 5] += rng.poisson(mean * profile)
        name = os.path.join(args.directory, f"synth_{i + 1:05d}.cbf")
        write_minicbf(name, image, phi0, args.osc, args)
        print(name)


if __name__ == "__main__":
    main()
