# Music.AI - Python SDK

This is a Python client library for the Music.AI API. For more information on the API and its capabilities, see the [API documentation](https://music.ai/docs/getting-started/introduction/).

### Quick start

Here's how you can easily create a job, wait for its completion, process it against the `music-ai/generate-chords` workflow, and then delete it:

```python
from musicai_sdk import MusicAiClient


music_ai = MusicAiClient(api_key="your-api-key")

song_url = music_ai.upload_file("./song.mp3")

job_id = music_ai.add_job(
    "My first job",
    "music-ai/generate-chords",
    {
        "inputUrl": song_url,
    },
)["id"]

job = music_ai.wait_for_job_completion(job_id)

if job["status"] == "SUCCEEDED":
    files = music_ai.download_job_results(job, "./chords")
    print("Result:", files)
else:
    print("Job failed!")

music_ai.delete_job(job_id)
```

## Installation

You can install the library via pip:

```bash
pip install musicai_sdk
```

## API Reference

### Types

```python
from typing import Optional, Dict
from dataclasses import dataclass

@dataclass
class Job:
    id: str
    app: str
    workflow: str
    status: str  # Could validate values separately
    batchName: Optional[str]
    workflowParams: Dict[str, str]
    metadata: Dict[str, str]
    result: Dict[str, str]
    name: str
    createdAt: str
    startedAt: str
    completedAt: Optional[str]
```

### Upload file

Uploads a local file to our temporary file server. Returns an temporary download URL you can use on other methods.

```python
def upload_file(file_path: str) -> str
```

#### Example

```python
song_url = music_ai.upload_file(file_path)
```

### Add a job

Creates a new job and returns its correponding ID.

```python
def add_job(job_name: str, workflow_slug: str, params: Dict[str, str]) -> str
```

#### Example

```python
song_url = "https://your-website.com/song.mp3"
job_id = music_ai.add_job(
    "job-1",
    "music-ai/generate-chords",
    {
        "inputUrl": song_url
    }
)
```

Check the [documentation](https://music.ai/docs) for all the existing workflows and expected correspondent parameters.

### Get a job

Gets a job information by its `id`.

```python
def get_job(job_id: str) -> Job
```

#### Example

```python
job = music_ai.get_job("your-job-id")
```

The `job` variable value:

```json
{
  "id": "2e35babc-91c4-4121-89f4-5a2acf956b28",
  "app": "Your app name",
  "workflow": {
    "id": "2ae5eea3-63dd-445e-9a3f-ff0473e82fd2",
    "name": "Stems Isolations - Vocals & accompaniments"
  },
  "status": "SUCCEEDED",
  "batchName": null,
  "workflowParams": {
    "inputUrl": "https://your-server.com/audio-input.m4a"
  },
  "metadata": {},
  "result": {
    "vocals": "https://cdn.music.ai/something/vocals.wav",
    "accompaniments": "https://cdn.music.ai/something/accompaniments.wav"
  },
  "name": "My job 123",
  "createdAt": "2022-12-07T19:21:42.170Z",
  "startedAt": "2022-12-07T19:21:42.307Z",
  "completedAt": "2022-12-07T19:22:00.325Z"
}
```

### List jobs

Return all existing jobs associated with the provided `api_key`. You can optionally filter by `status` and `workflow`:

```python
Status = Literal["QUEUED", "STARTED", "SUCCEEDED", "FAILED"]

class Filters(TypedDict, total=False):
    status: Optional[List[Status]]
    workflow: Optional[List[str]]

def list_jobs(filters: Optional[Filters] = None) -> List[Job]
```

#### Example

```python
jobs = music_ai.list_jobs()
```

```python
filters = {
    "status": ["SUCCEEDED", "FAILED"],
    "workflow": ["workflow-a", "workflow-b"]
}
jobs = music_ai.list_jobs(filters=filters)
```

### Delete a job

Delete a job by its `id`.

```python
delete_job(job_id: str) -> None
```

### Wait for a job completion

Waits until the job status is either `SUCCEEDED` or `FAILED`, and returns its information.

```python
def wait_for_job_completion(job_id: str) -> Job
```

#### Example

```python
job = music_ai.wait_for_job_completion("your-job-id")

if job["status"] == "SUCCEEDED":
    print("Job succeeded!")
else:
    print("Job failed!")
```

### Download all job results

Download all the job results to a local folder.

```python
def download_job_results(job_id_or_job_data: Union[str, Job], output_folder: str) -> List[str]
```

This function also creates a file called `workflow.results.json` containing the result in the JSON format. When an output is a file, that field will contain the relative path to the file.

#### Example

```python
result_paths = music_ai.download_job_results("your-job-id", "./results")
```

Or, if you already have the job object...

```python
job = music_ai.wait_for_job_completion("your-job-id")
result_paths = music_ai.download_job_results(job, "./results")
```

If the workflow has two outputs, vocals in WAVE format and bpm, two files will be created at the given folder: `vocals.wav` and `workflow.results.json`.

```json
// workflow.result.json

{
  "vocals": "./vocals.wav",
  "bpm": "64"
}
```
