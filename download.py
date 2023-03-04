import requests

from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
from db import DatabaseConnection
from pathlib import Path


def create_folder_structure(default_home):
    db = DatabaseConnection()
    authors = db.get_authors()
    for author in authors:
        Path(default_home + "/{}".format(author)).mkdir(parents=True, exist_ok=True)


def download_files(default_home):
    def pull_by_url(url_author_pair):
        resp = requests.get(url=url_author_pair[1])
        return resp, url_author_pair[0]

    db = DatabaseConnection()
    url_authors = db.get_urls_and_authors()

    with ThreadPoolExecutor() as executor:
        futures = []

        for pair in url_authors:
            futures.append(executor.submit(pull_by_url, url_author_pair=pair))

        for future in as_completed(futures):
            pair_result = future.result()
            result = pair_result[0]
            author_name = pair_result[1]
            url = urlparse(result.url)
            if result.status_code == 200:
                print("result from {} came back 200".format(url))
                if url.path.split(".")[1] != "m3u8":
                    filename = url.path.split("/")[-1]
                    with Path(default_home + "/{}/{}".format(author_name, filename)).open("wb") as f:
                        print("writing to {}".format(f.name))
                        for chunk in result:
                            f.write(chunk)
                else:
                    print("Not downloading m3u8 file")
            else:
                print("Not found: {}".format(url.geturl()))


if __name__ == '__main__':
    download_path = input("Where should this download to?")
    create_folder_structure(download_path)
    download_files(download_path)
