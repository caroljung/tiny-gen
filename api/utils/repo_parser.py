import requests
import logging
import os

MAX_FILE_SIZE = 10000

def scrape_github_repository(repo_url):
    # Split the repository URL to extract the username and repository name
    parts = repo_url.strip('/').split('/')
    if parts[2] != 'github.com':
        raise ValueError("Invalid GitHub repository URL.")

    username, repo_name = parts[3], parts[4]

    # Create the API URL to retrieve the repository contents
    root_content_url = f"https://api.github.com/repos/{username}/{repo_name}/contents"
    url_queue = [root_content_url]
    token = os.environ.get("GITHUB_TINYGEN_ACCESS_TOKEN")
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    try:
        repo_contents = ""      
        while url_queue:
          api_url = url_queue.pop()
          response = requests.get(api_url, headers=headers)
          response.raise_for_status()
          contents = response.json()

          for item in contents:
            logging.info(item)
            if item['type'] == 'file' and item['size'] <= MAX_FILE_SIZE:
                # Stream the content of each file and write it to the output file
                file_url = item['download_url']
                file_response = requests.get(file_url)
                file_response.raise_for_status()
                code = file_response.text
                
                repo_contents += f"----\n{item['path']}\n"
                repo_contents += f"{code}\n\n"

            elif item['type'] == 'dir':
              # Recursively scrape subdirectories
              url_queue.append(f"{root_content_url}/{item['path']}")
                    
        return repo_contents

    except requests.exceptions.RequestException as e:
        raise ValueError(str(e))
