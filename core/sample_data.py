import io
import numpy as np
import pandas as pd


def generate_sample_data(
    n_assets: int = 72,
    days: int = 14,
    freq: str = "h",
    seed: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    timestamps = pd.date_range(
        start="2026-04-01 00:00:00",
        periods=days * 24,
        freq=freq,
    )

    asset_types = ["CPU Server", "GPU Node", "Storage Node", "Network Device"]
    groups = ["Rack-A", "Rack-B", "Rack-C", "Rack-D", "Zone-1", "Zone-2"]

    records = []

    for i in range(1, n_assets + 1):
        asset_id = f"srv-{i:03d}"
        asset_type = rng.choice(asset_types, p=[0.55, 0.18, 0.17, 0.10])
        group = rng.choice(groups)

        if asset_type == "GPU Node":
            power_idle = rng.uniform(450, 750)
            power_peak = rng.uniform(1300, 2600)
        elif asset_type == "Storage Node":
            power_idle = rng.uniform(180, 350)
            power_peak = rng.uniform(350, 650)
        elif asset_type == "Network Device":
            power_idle = rng.uniform(120, 260)
            power_peak = rng.uniform(250, 550)
        else:
            power_idle = rng.uniform(150, 300)
            power_peak = rng.uniform(350, 700)

        behavior = rng.choice(
            ["normal", "busy", "low", "zombie"],
            p=[0.48, 0.18, 0.22, 0.12],
        )

        for ts in timestamps:
            hour = ts.hour
            daily_factor = 1.0 + 0.25 * np.sin((hour - 8) / 24 * 2 * np.pi)

            if behavior == "busy":
                base = rng.normal(55, 13) * daily_factor
            elif behavior == "normal":
                base = rng.normal(32, 12) * daily_factor
            elif behavior == "low":
                base = rng.normal(13, 6) * daily_factor
            else:
                base = rng.normal(4, 2)

            if rng.random() < 0.015 and behavior != "zombie":
                base += rng.uniform(35, 60)

            utilization = float(np.clip(base, 0, 100))
            memory_utilization = float(np.clip(utilization * rng.uniform(0.6, 1.4) + rng.normal(8, 8), 0, 100))
            network_io = float(np.clip(utilization * rng.uniform(0.2, 0.9) + rng.normal(5, 5), 0, 100))
            disk_io = float(np.clip(utilization * rng.uniform(0.2, 0.8) + rng.normal(5, 5), 0, 100))

            business_critical = rng.choice(["No", "Yes"], p=[0.82, 0.18])
            migratable = rng.choice(["Yes", "No"], p=[0.76, 0.24])

            records.append(
                {
                    "timestamp": ts,
                    "asset_id": asset_id,
                    "utilization": round(utilization, 2),
                    "asset_type": asset_type,
                    "group": group,
                    "power_idle": round(power_idle, 2),
                    "power_peak": round(power_peak, 2),
                    "memory_utilization": round(memory_utilization, 2),
                    "network_io": round(network_io, 2),
                    "disk_io": round(disk_io, 2),
                    "business_critical": business_critical,
                    "migratable": migratable,
                }
            )

    return pd.DataFrame(records)


def sample_csv_bytes() -> bytes:
    df = generate_sample_data()
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, encoding="utf-8-sig")
    return buffer.getvalue().encode("utf-8-sig")