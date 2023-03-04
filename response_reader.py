from tweepy.client import Response


def read_twitter_response(response: Response):
    results = []

    for raw_tweet in response.data:
        refined_tweet = {
            "unique_id": "tweet-{}".format(raw_tweet.id),
            "created_date": raw_tweet.created_at,
            "author_id": raw_tweet.author_id,
            "media_keys": raw_tweet.attachments["media_keys"] if raw_tweet.attachments else "",
            "text_body": raw_tweet.text
        }

        # Pull in the media
        media = [m for m in response.includes["media"] if m["data"]["media_key"] in refined_tweet["media_keys"]]
        if media:  # some posts may not have anything
            photos = []  # may have more than one photo (think tile quadrant)
            for record in media:
                if record.type == 'photo':
                    # only photo, no variants
                    photos.append(record.url)
                else:
                    # Animated GIF or video, has variants, capture them all
                    variants = []
                    for variant in record.variants:
                        variants.append(variant["url"])
                    refined_tweet["video_urls"] = variants
            refined_tweet["image_urls"] = photos

        # Identify the author
        # This is unique per call, several posts may have the same author
        author = [u for u in response.includes["users"] if u.id == refined_tweet["author_id"]][0]
        refined_tweet["display_name"] = author.username
        # Extract URLs from author
        urls = extract_urls_from_author(author)
        author_data = {
            "username": author.name,
            "urls": list(urls)
        }
        refined_tweet["author_metadata"] = author_data
        results.append(refined_tweet)

    return results


def extract_urls_from_author(author: any) -> set:
    urls = set()
    if author.entities:
        entities = author.entities
        if "url" in entities:
            url_entities = entities["url"]
            if "urls" in url_entities:
                for url in url_entities["urls"]:
                    urls.add(url["expanded_url"])
        if "description" in entities:
            description_entities = entities["description"]
            if "urls" in description_entities:
                for url in description_entities["urls"]:
                    urls.add(url["expanded_url"])
    return urls
