def cpu_to_watts(cpu_percent: float, tdp: int) -> float:
    """ CPU 사용률을 전력(W)으로 변환 """
    if cpu_percent < 0 or cpu_percent > 100:
        raise ValueError(f"cpu_percent error: {cpu_percent}")
    return cpu_percent * tdp / 100


def watts_to_kwh(watts: float, duration_sec: int) -> float:
    """ 전력(W)과 시간(초)을 받아서 kWh 반환 """
    if watts < 0:
        raise ValueError(f"Watts error: {watts}")
    if duration_sec <= 0:
        raise ValueError(f"Time error: {duration_sec}")
    return watts * duration_sec / 3600 / 1000


def kwh_to_co2(kwh: float, pue: float, carbon_intensity: float) -> float:
    """ kWh와 PUE, 탄소강도를 받아서 gCO₂ 반환 """
    if kwh < 0:
        raise ValueError(f"kwh error: {kwh}")
    if pue < 1.0:
        raise ValueError(f"PUE error: {pue}")
    if carbon_intensity < 0:
        raise ValueError(f"carbon_intensity error: {carbon_intensity}")
    return kwh * pue * carbon_intensity