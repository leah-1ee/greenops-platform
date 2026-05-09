from converter import cpu_to_watts, watts_to_kwh, kwh_to_co2

# 정상 시나리오
# t3.medium 인스턴스에서 CPU 50% 사용 중, 서울 리전
watts = cpu_to_watts(50.0, 15)         # t3.medium TDP = 15W
print(f"전력: {watts}W")               # 7.5W 예상

kwh = watts_to_kwh(watts, 15)          # 15초 동안
print(f"전력량: {kwh}kWh")

co2 = kwh_to_co2(kwh, 1.15, 415)       # 서울 PUE=1.15, 강도=415
print(f"탄소: {co2}g")