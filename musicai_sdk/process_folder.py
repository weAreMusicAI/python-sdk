import logging
import os
import time
import requests
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def process_file(client, file_path, output_folder, workflow_id, delete=True, failed_file=None):
    # Upload local file
    file_url = client.upload_file(file_path=file_path)

    # Create Job
    workflow_params = {
        'inputUrl': file_url,
    }
    add_job_info = client.add_job(job_name=os.path.basename(file_path), workflow_slug=workflow_id, params=workflow_params)
    job_id = add_job_info['id']
    file_name = os.path.basename(file_path)
    logger.info(f"Job Created for {file_name} with id {job_id}")
    

    # Polling for job results
    while True:
        try:
            job_info = client.get_job(job_id=job_id)
        except Exception as e:
            logger.error(f"Failed to get job info for {file_name}: {e}")
            time.sleep(5)
            continue
        if job_info['status'] == 'SUCCEEDED':
            break
        if job_info['status'] == 'FAILED':
            logger.error(f"Job for {file_name} failed")
            # create failed.json file if it does not exist
            if not os.path.exists(failed_file):
                with open(failed_file, 'w') as f:
                    f.write('')
            # Save failed file
            with open(failed_file, 'a') as f:
                f.write(file_path + '\n')
            break
        logger.info(f"Waiting for job completion for {file_name}")
        time.sleep(5)

    logger.info(f"Job completed with status {job_info['status']} for {file_name}")

    # Download the result
    result = job_info['result']

    # for all elements in the result, download them if it start with http
    for key, value in result.items():
        if value.startswith('http'):
            # remove query params from url
            url_clean = value.split('?')[0]
            extension = os.path.splitext(url_clean)[1]
            response = requests.get(value)
            output_file_name = os.path.join(os.path.splitext(os.path.basename(file_path))[0], key)
            output_path = os.path.join(output_folder, output_file_name + extension)
            # Create the output folder if it does not exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)

    logger.info(f"Job result downloaded for {file_name}")
    if delete:
        client.delete_job(job_id=job_id)
        logger.info(f"Job for {file_name} deleted from server")

def process_folder(input_folder, output_folder, workflow_id, parallelism=5, delete=True, client=None):
    # add failed.json file to output_folder to control all failed files
    failed_file = os.path.join(output_folder, 'failed.json')
    with ThreadPoolExecutor(max_workers=parallelism) as executor:
        for file_name in os.listdir(input_folder):
            # Skip hidden files and folders
            if file_name.startswith('.'):
                continue
            if not os.path.isfile(os.path.join(input_folder, file_name)):
                continue
            file_path = os.path.join(input_folder, file_name)
            executor.submit(process_file, client, file_path, output_folder, workflow_id, delete, failed_file)

# Example usage
# client = MusicAiClient(api_key='your api key')
# folder_path = '/path/to/your/folder'
# output_folder = '/path/to/output/folder'
# workflow_id = 'your_workflow_id'
# process_folder_with_workflow(folder_path, output_folder, workflow_id, client=client, parallelism=5, delete=True)
