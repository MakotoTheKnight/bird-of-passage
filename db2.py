import sqlite3
from sqlite3 import Cursor

from yoyo import get_backend, read_migrations


class DatabaseConnection:
    def __init__(self, db_name="bop2.sqlite"):
        self.db = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        backend = get_backend("sqlite:///{}".format(db_name))
        migrations = read_migrations("../migrations")

        with backend.lock():
            backend.apply_migrations(backend.to_apply(migrations))

    def insert_into_database(self, results: list) -> None:
        cursor = self.db.cursor()
        for record in results:
            self._insert_single_record(record, cursor)
        self.db.commit()
        cursor.close()

    def _insert_single_record(self, record: dict, cursor: Cursor) -> None:
        cursor.execute("insert into author(display_name) values (?) on conflict do nothing",
                       (record["display_name"],))

        expanded_profile_links = [(record["display_name"], link) for link in record["author_metadata"]["urls"]]

        cursor.executemany(
            "insert into author_links(author_display_name, profile_link) values (?, ?) on conflict do nothing",
            expanded_profile_links
        )
        if "image_urls" in record:
            expanded_photo_data = [(record["unique_id"], record["display_name"], url, "image", record["created_date"])
                                   for url in record["image_urls"]]
            cursor.executemany(
                """insert into tweet_media(tweet_data_id, author_display_name, media_url, media_type, created_date)
                values (?, ?, ?, ?, ?)
                on conflict do nothing""",
                expanded_photo_data)

        if "video_urls" in record:
            expanded_video_data = [(record["unique_id"], record["display_name"], url, "video", record["created_date"])
                                   for url in record["video_urls"]]
            cursor.executemany(
                """insert into tweet_media(tweet_data_id, author_display_name, media_url, media_type, created_date)
                values (?, ?, ?, ?, ?)
                on conflict do nothing""",
                expanded_video_data)

        cursor.execute(
            """insert into tweet_body(tweet_data_id, author_display_name, tweet_body, created_date) values (?, ?, ?, ?)
            on conflict do nothing""",
            (record["unique_id"], record["display_name"], record["text_body"], record["created_date"]))
