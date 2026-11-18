"""Free Arabic TTS: Piper phonemizer (GitHub) + ar_JO-kareem voice, run with onnxruntime.
usage: python3 say.py out.wav "النص" [length_scale]"""
import json, subprocess, sys, wave, os
import numpy as np, onnxruntime as ort

D = os.path.dirname(os.path.abspath(__file__))
MODEL = f"{D}/vits-piper-ar_JO-kareem-medium/ar_JO-kareem-medium.onnx"
CFG = json.load(open(MODEL + ".json"))
_sess = None


def phonemize(text):
    p = subprocess.run([f"{D}/piper/piper_phonemize", "-l", "ar", "--espeak_data", f"{D}/piper/espeak-ng-data",
                        "--tashkeel_model", f"{D}/piper/libtashkeel_model.ort"],
                       input=text, capture_output=True, text=True, env={**os.environ, "LD_LIBRARY_PATH": f"{D}/piper"}, check=True)
    return [json.loads(l)["phoneme_ids"] for l in p.stdout.splitlines() if l.strip()]


def synth(text, length_scale=1.08, noise=0.667, noise_w=0.8):
    global _sess
    _sess = _sess or ort.InferenceSession(MODEL, providers=["CPUExecutionProvider"])
    out = []
    sr = CFG["audio"]["sample_rate"]
    for ids in phonemize(text):
        a = np.array([ids], dtype=np.int64)
        audio = _sess.run(None, {"input": a, "input_lengths": np.array([a.shape[1]], dtype=np.int64),
                                 "scales": np.array([noise, length_scale, noise_w], dtype=np.float32)})[0].squeeze()
        out.append(audio)
        out.append(np.zeros(int(sr * 0.25), dtype=np.float32))
    return np.concatenate(out), sr


def write(path, audio, sr):
    audio = audio / max(1e-6, np.abs(audio).max()) * 0.9
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((audio * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    a, sr = synth(sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 1.08)
    write(sys.argv[1], a, sr)
    print(sys.argv[1], round(len(a) / sr, 2), "s")
