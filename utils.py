import os

from dotenv import load_dotenv
import torch
import torchaudio
from pyannote.audio import Pipeline

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")

ROOT = os.getcwd()

pipeline = Pipeline.from_pretrained(
    "pyannote/overlapped-speech-detection", use_auth_token=API_TOKEN
)


def sampleIdx(sec, samplerate):
    return int(sec * samplerate)


def timestampToFrameIndices(output, samplerate):
    overlaps = [(start, end) for start, end in output.get_timeline().support()]

    indices = []
    for start, end in overlaps:
        start_frame = sampleIdx(start, samplerate)
        end_frame = sampleIdx(end, samplerate)
        indices.append((start_frame, end_frame))
    return indices


def wavSegment(waveform, startFrame, endFrame=None):
    return waveform[0:, startFrame:endFrame]


def mergeWaveforms(wavList):
    segments = tuple(wavList)
    merged = torch.cat(segments, 1)
    return merged


def saveAudio(outpath, waveform, samplerate):
    torchaudio.save(outpath, waveform, sample_rate=samplerate, bits_per_sample=16)


def getOverlap(audio_path):
    output = pipeline(audio_path)
    waveform, samplerate = torchaudio.load(audio_path)
    indices = timestampToFrameIndices(output, samplerate)
    return (output, indices)


def waveformFromIndices(indices, waveform):
    wavlist = [wavSegment(waveform, start, end) for start, end in indices]
    return mergeWaveforms(wavlist)


def nonOverlapping(overlapIndices, waveform):
    segments = []
    idx = 0

    for start, end in overlapIndices:
        segment = wavSegment(waveform, idx, start - 1)
        segments.append(segment)
        idx = end + 1
    lastSegment = wavSegment(waveform, idx)
    segments.append(lastSegment)

    merged = mergeWaveforms(segments)
    return merged


def getCleanAudio(audio_path, pipeline):
    output = pipeline(audio_path)
    waveform, samplerate = torchaudio.load(audio_path)
    indices = timestampToFrameIndices(output, samplerate)
    cleanAudio = nonOverlapping(indices, waveform)
    return (cleanAudio, samplerate)
