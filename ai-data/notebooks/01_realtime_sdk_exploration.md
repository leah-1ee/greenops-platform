# Week 1: Carbon Aware SDK 탐색 및 데이터 소스 결정

## 1. 시도한 데이터 소스
- WattTime: 무료 계정 1 권역(CAISO_NORTH)만 가능 → 멀티리전 시연 어려움
- WattTime 학생 계정 -> 많은 지역 사용 가능 / 좀 더 정확한 데이터 / 한국 사용 불가
- ElectricityMaps: 무료 1 zone 가능, 학생 계정으로 추가 3가지 zone 신청 가능

## 2. 최종 결정: ElectricityMaps
- 이유: 멀티리전 가능성, Carbon Aware SDK 정식 지원
- 한계: average emissions만 제공 (marginal X)
- 활성 zone: KR (한국, koreacentral 매핑)

## 3. 호출 결과 샘플
curl -i "http://localhost:5073/emissions/bylocation?location=koreacentral&time=2026-04-01T00:00:00Z&toTime=2026-04-02T00:00:00Z"
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Date: Sat, 16 May 2026 13:12:41 GMT
Server: Kestrel
Transfer-Encoding: chunked

[{"location":"koreacentral","time":"2026-04-01T00:00:00+00:00","rating":416,"duration":"01:00:00"},{"location":"koreacentral","time":"2026-04-01T01:00:00+00:00","rating":502,"duration":"01:00:00"},{"location":"koreacentral","time":"2026-04-01T02:00:00+00:00","rating":409,"duration":"01:00:00"},{"location":"koreacentral","time":"2026-04-01T03:00:00+00:00","rating":539,"duration":"01:00:00"},{"location":"koreacentral","time":"2026-04-01T04:00:00+00:00","rating":337,"duration":"01:00:00"},{"location":"koreacentral","time":"2026-04-01T05:00:00+00:00","rating":544,"duration":"01:00:00"},{"location":"koreacentral","time":"2026-04-01T06:00:00+00:00","rating":347,"duration":"01:00:00"},{"location":"koreacentral","time":"2026-04-01T07:00:00+00:00","rating":522,"duration":"01:00:00"},{"location":"koreacentral","time":"2026-04-01T08:00:00+00:00","rating":433,"duration":"01:00:00"},{"location":"koreacentral","time":"2026-04-01T09:00:00+00:00","rating":532,"duration":"01:00:00"},{"location":"koreacentral","time":"2026-04-01T10:00:00+00:00","rating":523,"duration":"01:00:00"},{"location":"koreacentral","time":"2026-04-01T11:00:00+00:00","rating":368,"duration":"01:00:00"},{"location":"koreacentral","time":"2026-04-01T12:00:00+00:00","rating":438,"duration":"01:00:00"},{"location":"koreacentral","time":"2026-04-01T13:00:00+00:00","rating":407,"duration":"01:00:00"},{"location":"koreacentral","time":"2026-04-01T14:00:00+00:00","rating":514,"duration":"01:00:00"},{"location":"koreacentral","time":"2026-04-01T15:00:00+00:00","rating":537,"duration":"01:00:00"},{"location":"koreacentral","time":"2026-04-01T16:00:00+00:00","rating":397,"duration":"01:00:00"},{"location":"koreacentral","time":"2026-04-01T17:00:00+00:00","rating":475,"duration":"01:00:00"},{"location":"koreacentral","time":"2026-04-01T18:00:00+00:00","rating":530,"duration":"01:00:00"},{"location":"koreacentral","time":"2026-04-01T19:00:00+00:00","rating":335,"duration":"01:00:00"},{"location":"koreacentral","time":"2026-04-01T20:00:00+00:00","rating":373,"duration":"01:00:00"},{"location":"koreacentral","time":"2026-04-01T21:00:00+00:00","rating":340,"duration":"01:00:00"},{"location":"koreacentral","time":"2026-04-01T22:00:00+00:00","rating":389,"duration":"01:00:00"},{"location":"koreacentral","time":"2026-04-01T23:00:00+00:00","rating":413,"duration":"01:00:00"}]

## 4. 다음 단계
- 학생 계정 zone 추가
- forecast 미지원 → 자체 forecaster.py로 보완 (Week 2~3)
