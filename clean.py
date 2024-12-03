import os
import time
import logging

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("logs.txt"), stream_handler],
)

from utils import pipeline, getCleanAudio, saveAudio


def getFiles(dir):
    dirs = [(os.path.join(dir, subdir), subdir) for subdir in os.listdir(dir)]

    files = [
        (os.path.join(subdir, file), dir, file)
        for subdir, dir in dirs
        for file in os.listdir(subdir)
    ]
    return sorted(files)


def getFilenames(dir):
    dirs = [(os.path.join(dir, subdir), subdir) for subdir in os.listdir(dir)]

    files = [
        os.path.join(dir, subdir, file)
        for subdir, dir in dirs
        for file in os.listdir(subdir)
    ]
    return sorted(files)


ROOT = os.getcwd()

audioDir = os.path.join(ROOT, "audio")
outputDir = os.path.join(ROOT, "clean")

os.makedirs(outputDir, exist_ok=True)

files = getFiles(audioDir)

for file in files:
    filepath, showname, filename = file
    start_time = time.time()
    completed = getFilenames(outputDir)
    output_dir = os.path.join(outputDir, showname)
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.join(output_dir, filename)
    if output_filename not in completed:
        cleanAudio, samplerate = getCleanAudio(filepath, pipeline)
        saveAudio(output_filename, cleanAudio, samplerate)
        execution_time = time.time() - start_time
        logging.info(f"{showname}/{filename}|{execution_time}")
