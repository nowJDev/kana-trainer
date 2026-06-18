# Kana Trainer

일본어 직접 입력 없이 히라가나와 가타카나를 연습하는 CLI 학습 앱입니다.

## 실행

```powershell
python -m kana_trainer
```

Windows에서는 같은 폴더의 배치 파일로 바로 실행할 수 있습니다.

```powershell
.\run-kana-trainer.bat
```

입력 없는 데모는 다음처럼 볼 수 있습니다.

```powershell
python -m kana_trainer --demo
```

## 학습 모드

- 히라가나 보고 로마자 입력.
- 가타카나 보고 로마자 입력.
- 로마자 보고 히라가나 4지선다 선택.
- 히라가나-가타카나 매칭.
- 틀린 문자 오답 복습.
- `일본어.md`의 헷갈리는 쌍, 촉음 예문, 읽기 예문, 조사 참고 자료 보기.
- `일본어.md` 원문 전체 보기.

오답 기록은 기본적으로 사용자 홈의 `.kana-trainer/wrong-answers.json`에 저장됩니다. 다른 위치를 쓰려면 `KANA_TRAINER_WRONG_PATH` 환경변수를 설정하면 됩니다.
