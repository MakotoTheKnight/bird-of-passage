from datetime import datetime

import jmespath
from cerberus import Validator


class DateTimeNormalizingValidator(Validator):
    def __init__(self, *args, **kwargs):
        super(DateTimeNormalizingValidator, self).__init__(*args, **kwargs)

    def _normalize_coerce_convert_to_datetime(self, value):
        """
        # Insert in basic tweet data
        # Tue Nov 15 07:47:01 +0000 2022
        # %a %b %d %H:%M:%S %z %Y

        :param value: unparsed value in the format of %a %b %d %H:%M:%S %z %Y (Tue Nov 15 07:47:01 +0000 2022)
        :return: a datetime representing the actual time
        """
        return datetime.strptime(value, "%a %b %d %H:%M:%S %z %Y")


def cursor_validator(field, value, error):
    if "cursor-" in value:
        error(field, "cursor-* IDs are rejected...for now...")


parsed_tweet_structure = {
    "unique_id": {"type": "string", "nullable": False, "check_with": cursor_validator},
    "created_date": {"type": "datetime", "nullable": False, "coerce": "convert_to_datetime"},
    "display_name": {"type": "string", "nullable": False},
    "profile_links_1": {"type": "list", "nullable": False, "schema": {"type": "string"},
                        "default_setter": lambda _: []},
    "profile_links_2": {"type": "list", "nullable": False, "schema": {"type": "string"},
                        "default_setter": lambda _: []},
    "image_urls": {"type": "list", "nullable": False, "schema": {"type": "string"},
                   "default_setter": lambda _: []},
    "video_urls": {"type": "list", "nullable": False, "schema": {"type": "string"},
                   "default_setter": lambda _: []},
    "text_body": {"type": "string", "nullable": False}
}

validator = DateTimeNormalizingValidator(parsed_tweet_structure)


def parse_json(unrefined_json_struct: dict) -> list:
    result = jmespath.search("""
    data.bookmark_timeline.timeline.instructions[].entries[].{
              unique_id: entryId,
              created_date: content.itemContent.tweet_results.result.legacy.created_at,
              display_name: content.itemContent.tweet_results.result.core.user_results.result.legacy.screen_name,
              profile_links_1: content.itemContent.tweet_results.result.core.user_results.result.legacy.entities.description.urls[].expanded_url,
              profile_links_2: content.itemContent.tweet_results.result.core.user_results.result.legacy.entities.url.urls[].expanded_url,
              image_urls: content.itemContent.tweet_results.result.legacy.extended_entities.media[].media_url_https,
              video_urls: content.itemContent.tweet_results.result.legacy.extended_entities.media[].video_info.variants[].url,
              text_body: content.itemContent.tweet_results.result.legacy.full_text
            }
    """, unrefined_json_struct)
    return_value = []
    if result:
        for json in result:
            if validator.validate(json):
                return_value.append(validator.normalized(json))
    else:
        # Looks like this is just some error JSON that isn't read; safe to ignore.
        pass
    return return_value
