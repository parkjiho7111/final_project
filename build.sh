#!/bin/bash
set -e  # 오류 발생 시 즉시 중단

# pip 업그레이드
python3 -m pip install --upgrade pip

# 의존성 설치
python3 -m pip install -r requirements.txt
