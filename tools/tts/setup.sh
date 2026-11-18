#!/usr/bin/env bash
# أداة صوت مجانية للتعليق التجريبي: Piper (GitHub) + صوت عربي ar_JO-kareem (من إصدارات sherpa-onnx على GitHub)
# التشغيل يحتاج onnxruntime و numpy في بايثون.
set -e
cd "$(dirname "$0")"
curl -sSL -o piper.tgz https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz
curl -sSL -o kareem.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-ar_JO-kareem-medium.tar.bz2
tar xzf piper.tgz && tar xjf kareem.tar.bz2 && rm piper.tgz kareem.tar.bz2
echo 'جاهز: python3 say.py out.wav "النص"'
