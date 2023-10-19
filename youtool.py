import datetime
import re
from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from typing import List
from urllib.parse import urljoin, urlparse

import isodate
import requests

REGEXP_CHANNEL_ID = re.compile('"externalId":"([^"]+)"')
REGEXP_LOCATION_RADIUS = re.compile(r"^[0-9.]+(?:m|km|ft|mi)$")


def cleanup(data):
    """Remove NUL (\x00) from str, dict e lists, recursively

    >>> cleanup("a\\x00b")
    'ab'
    >>> cleanup(["a\\x00b", "c\\x00d"])
    ['ab', 'cd']
    >>> cleanup({"a": "a\\x00b", "b": "c\\x00d"})
    {'a': 'ab', 'b': 'cd'}
    >>> cleanup({"a": "a\\x00b", "b": {"b1": 1, "b2": "c\\x00d"}})
    {'a': 'ab', 'b': {'b1': 1, 'b2': 'cd'}}
    >>> cleanup({"a": "a\\x00b", "b": {"b1": 1, "b2": "c\\x00d"}, "c": 1, "d": 3.14})
    {'a': 'ab', 'b': {'b1': 1, 'b2': 'cd'}, 'c': 1, 'd': 3.14}
    """

    if isinstance(data, str):
        return data.replace("\x00", "").strip()
    elif isinstance(data, list):
        return [cleanup(item) for item in data]
    elif isinstance(data, dict):
        return {key: cleanup(value) for key, value in data.items()}
    else:
        return data


def ipartition(iterable, partition_size):  # Copied from <https://github.com/turicas/rows/>
    if not isinstance(iterable, Iterator):
        iterator = iter(iterable)
    else:
        iterator = iterable

    finished = False
    while not finished:
        data = []
        for _ in range(partition_size):
            try:
                data.append(next(iterator))
            except StopIteration:
                finished = True
                break
        if data:
            yield data


def parse_int(value):
    """
    >>> str(parse_int(''))
    'None'
    >>> str(parse_int(None))
    'None'
    >>> parse_int('2022')
    2022
    """
    value = str(value or "").strip()
    if not value:
        return None
    return int(value)


def parse_decimal(value):
    """
    >>> str(parse_decimal(''))
    'None'
    >>> str(parse_decimal(None))
    'None'
    >>> parse_decimal('3.14')
    Decimal('3.14')
    >>> parse_decimal(3)
    Decimal('3')
    >>> parse_decimal(3.14)
    Decimal('3.14')
    """
    value = str(value or "").strip()
    if not value:
        return None
    return Decimal(value)


def parse_datetime(value):
    """
    >>> str(parse_datetime(''))
    'None'
    >>> str(parse_datetime(None))
    'None'
    >>> parse_datetime('2022-01-15T01:02:03Z')
    datetime.datetime(2022, 1, 15, 1, 2, 3, tzinfo=datetime.timezone.utc)
    """
    value = str(value or "").strip()
    if not value:
        return None
    if value[-1] == "Z":
        value = value[:-1] + "+00:00"
    return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z")


def parse_timestamp(value):
    """
    >>> str(parse_timestamp(''))
    'None'
    >>> str(parse_timestamp(None))
    'None'
    >>> parse_timestamp(1697069683982633)
    datetime.datetime(2023, 10, 12, 0, 14, 43, 982633, tzinfo=datetime.timezone.utc)
    """
    value = str(value or "").strip()
    if not value:
        return None
    return datetime.datetime.fromtimestamp(int(value) / 1000000, tz=datetime.timezone.utc)


def parse_category_data(item):
    snippet = item["snippet"]
    return {
        "id": parse_int(item["id"]),
        "title": snippet["title"],
        "assignable": snippet["assignable"],
        "channel_id": snippet["channelId"],
    }


def parse_channel_data(item):
    stats = item["statistics"]
    snippet = item["snippet"]
    details = item["contentDetails"]
    return {
        "id": item["id"],
        "title": snippet.get("title"),
        "description": snippet.get("description"),
        "custom_username": snippet.get("customUrl"),
        "published_at": parse_datetime(snippet.get("publishedAt")),
        "thumbnail_url": snippet.get("thumbnails", {}).get("default", {}).get("url"),
        "views": parse_int(stats.get("viewCount")),
        "subscribers": parse_int(stats.get("subscriberCount")),
        "videos": parse_int(stats.get("videoCount")),
        "playlist_id": details["relatedPlaylists"]["uploads"],
    }


def parse_playlist_data(item):
    snippet = item["snippet"]
    details = item["contentDetails"]
    return {
        "id": item["id"],
        "title": snippet.get("title"),
        "description": snippet.get("description"),
        "videos": details["itemCount"],
        "channel_id": snippet.get("channelId"),
        "channel_title": snippet.get("channelTitle"),
        "published_at": parse_datetime(snippet.get("publishedAt")),
        "thumbnail_url": snippet.get("thumbnails", {}).get("default", {}).get("url"),
    }


def parse_video_data(item):
    video_stats = item.get("statistics", {}) or {}
    video_live = item.get("liveStreamingDetails", {}) or {}
    video_details = item.get("snippet", {}) or {}
    content_details = item.get("contentDetails", {}) or {}
    video_status = item.get("status", {}) or {}
    kind = item["kind"]

    # TODO: `item` will be different if it came from `videos`, `playlistItems` or `search` resources (`search` does not
    # provide most of the keys, for example). We may want to return other type (like a dataclass) and a different type
    # for each case, since the way it is now can be confusing (`dict` always with same keys, but with some with a lot
    # of `None` values.
    if kind == "youtube#video":  # Most complete video information
        video_id = item["id"]
        video_owner_channel_id = video_details.get("channelId")
        video_owner_channel_title = video_details.get("channelTitle")
        playlist_owner_channel_id = playlist_owner_channel_title = added_to_playlist_at = None
        published_at = parse_datetime(video_details.get("publishedAt"))
    elif kind == "youtube#playlistItem":  # Also contentDetails,snippet,status and playlist information
        # If it's a video from a playlist, the owner will be always the author of the video (not the playlist owner)
        assert (
            video_details["resourceId"]["kind"] == "youtube#video"
        ), f"Expecting 'youtube#video' as playlist item, found {repr(video_details['resourceId'])}"
        video_id = video_details["resourceId"]["videoId"]
        video_owner_channel_id = video_details.get("videoOwnerChannelId")
        video_owner_channel_title = video_details.get("videoOwnerChannelTitle")
        playlist_owner_channel_id = video_details.get("channelId")
        playlist_owner_channel_title = video_details.get("channelTitle")
        added_to_playlist_at = parse_datetime(video_details.get("publishedAt"))
        published_at = parse_datetime(content_details.get("videoPublishedAt"))
    elif kind == "youtube#searchResult":  # Less complete information (just `snippet`)
        video_id = item["id"]["videoId"]
        video_owner_channel_id = video_details.get("channelId")
        video_owner_channel_title = video_details.get("channelTitle")
        playlist_owner_channel_id = playlist_owner_channel_title = added_to_playlist_at = None
        published_at = parse_datetime(video_details.get("publishedAt"))
    else:
        raise ValueError(f"Unknown kind of video to parse: {kind}")

    # TODO: what to do with snippet/liveBroadcastContent? (currently ignoring)
    # TODO: what to do with snippet/localized? (currently ignoring)
    duration = content_details.get("duration")
    return cleanup(
        {
            "id": video_id,
            "duration": isodate.parse_duration(duration).total_seconds() if duration else None,
            "definition": content_details.get("definition"),
            "status": video_status.get("privacyStatus"),
            "views": parse_int(video_stats.get("viewCount")),
            "likes": parse_int(video_stats.get("likeCount")),
            "dislikes": parse_int(video_stats.get("dislikeCount")),
            "favorites": parse_int(video_stats.get("favoriteCount")),
            "comments": parse_int(video_stats.get("commentCount")),
            "scheduled_to": parse_datetime(video_live.get("scheduledStartTime")),
            "started_at": parse_datetime(video_live.get("actualStartTime")),
            "finished_at": parse_datetime(video_live.get("actualEndTime")),
            "concurrent_viewers": video_live.get("concurrentViewers"),
            "channel_id": video_owner_channel_id,
            "channel_title": video_owner_channel_title,
            "playlist_channel_id": playlist_owner_channel_id,
            "playlist_channel_title": playlist_owner_channel_title,
            "title": video_details.get("title"),
            "description": video_details.get("description"),
            "published_at": published_at,
            "added_to_playlist_at": added_to_playlist_at,
            "tags": video_details.get("tags"),
        }
    )


def parse_comment_data(item, replies=None):
    snippet = item["snippet"]
    return {
        "id": item["id"],
        "parent_id": snippet.get("parentId"),
        "video_id": snippet["videoId"],
        "text": snippet["textOriginal"],
        "author": snippet["authorDisplayName"],
        "author_profile_image_url": snippet["authorProfileImageUrl"],
        "author_channel_id": snippet["authorChannelId"]["value"],
        "likes": snippet.get("likeCount"),
        "published_at": parse_datetime(snippet["publishedAt"]),
        "updated_at": parse_datetime(snippet["updatedAt"]),
        "replies": replies,
    }


class YouTube:
    base_url = "https://youtube.googleapis.com/youtube/v3/"
    search_topics = {
        "Music (parent topic)": "/m/04rlf",  # Music
        "Christian music": "/m/02mscn",  # Music
        "Classical music": "/m/0ggq0m",  # Music
        "Country": "/m/01lyv",  # Music
        "Electronic music": "/m/02lkt",  # Music
        "Hip hop music": "/m/0glt670",  # Music
        "Independent music": "/m/05rwpb",  # Music
        "Jazz": "/m/03_d0",  # Music
        "Music of Asia": "/m/028sqc",  # Music
        "Music of Latin America": "/m/0g293",  # Music
        "Pop music": "/m/064t9",  # Music
        "Reggae": "/m/06cqb",  # Music
        "Rhythm and blues": "/m/06j6l",  # Music
        "Rock music": "/m/06by7",  # Music
        "Soul music": "/m/0gywn",  # Music
        "Gaming (parent topic)": "/m/0bzvm2",  # Gaming
        "Action game": "/m/025zzc",  # Gaming
        "Action-adventure game": "/m/02ntfj",  # Gaming
        "Casual game": "/m/0b1vjn",  # Gaming
        "Music video game": "/m/02hygl",  # Gaming
        "Puzzle video game": "/m/04q1x3q",  # Gaming
        "Racing video game": "/m/01sjng",  # Gaming
        "Role-playing video game": "/m/0403l3g",  # Gaming
        "Simulation video game": "/m/021bp2",  # Gaming
        "Sports game": "/m/022dc6",  # Gaming
        "Strategy video game": "/m/03hf_rm",  # Gaming
        "Sports (parent topic)": "/m/06ntj",  # Sports
        "American football": "/m/0jm_",  # Sports
        "Baseball": "/m/018jz",  # Sports
        "Basketball": "/m/018w8",  # Sports
        "Boxing": "/m/01cgz",  # Sports
        "Cricket": "/m/09xp_",  # Sports
        "Football": "/m/02vx4",  # Sports
        "Golf": "/m/037hz",  # Sports
        "Ice hockey": "/m/03tmr",  # Sports
        "Mixed martial arts": "/m/01h7lh",  # Sports
        "Motorsport": "/m/0410tth",  # Sports
        "Tennis": "/m/07bs0",  # Sports
        "Volleyball": "/m/07_53",  # Sports
        "Entertainment (parent topic)": "/m/02jjt",  # Entertainment
        "Humor": "/m/09kqc",  # Entertainment
        "Movies": "/m/02vxn",  # Entertainment
        "Performing arts": "/m/05qjc",  # Entertainment
        "Professional wrestling": "/m/066wd",  # Entertainment
        "TV shows": "/m/0f2f9",  # Entertainment
        "Lifestyle (parent topic)": "/m/019_rr",  # Lifestyle
        "Fashion": "/m/032tl",  # Lifestyle
        "Fitness": "/m/027x7n",  # Lifestyle
        "Food": "/m/02wbm",  # Lifestyle
        "Hobby": "/m/03glg",  # Lifestyle
        "Pets": "/m/068hy",  # Lifestyle
        "Physical attractiveness [Beauty]": "/m/041xxh",  # Lifestyle
        "Technology": "/m/07c1v",  # Lifestyle
        "Tourism": "/m/07bxq",  # Lifestyle
        "Vehicles": "/m/07yv9",  # Lifestyle
        "Society (parent topic)": "/m/098wr",  # Society
        "Business": "/m/09s1f",  # Society
        "Health": "/m/0kt51",  # Society
        "Military": "/m/01h6rj",  # Society
        "Politics": "/m/05qt0",  # Society
        "Religion": "/m/06bvp",  # Society
        "Knowledge": "/m/01k8wb",  # Other
    }

    def __init__(self, api_keys: List[str], disable_ipv6=False):
        self.__api_keys = list(api_keys)  # Consume and make a copy (it'll be `pop`ed)
        self.__current_key = self.__api_keys.pop(0)
        self.__params = {"key": self.__current_key, "maxResults": 50}  # 50 is the max for YouTube Data API v3
        self._ydls = {}
        self.disable_ipv6 = disable_ipv6
        if disable_ipv6:
            requests.packages.urllib3.util.connection.HAS_IPV6 = False
        self.session = requests.Session()

    def request(self, path, params=None):
        final_params = self.__params.copy()
        final_params.update(params or {})
        url = urljoin(self.base_url, path)

        response = self.session.get(url, params=final_params)
        data = response.json()
        while "error" in data and 400 <= data["error"]["code"] < 500:
            try:
                self.__current_key = self.__api_keys.pop(0)
            except IndexError:
                raise RuntimeError(f"Too many 4xx errors, tried all YouTube keys ({data['error']['errors']})")
            self.__params["key"] = final_params["key"] = self.__current_key
            response = self.session.get(url, params=final_params)
            data = response.json()
        return data

    def paginate(self, path, params=None):
        finished = False
        while not finished:
            response = self.request(path, params=params)
            yield from response["items"]
            next_page_token = response.get("nextPageToken")
            if next_page_token is None:  # Finished
                break
            params["pageToken"] = next_page_token

    def channel_id_from_url(self, url):
        """Scrapes HTML returned by URL to find the channel ID

        >>> YouTube([None]).channel_id_from_url('https://youtube.com/channel/somechannelid/?qs=test')
        'somechannelid'
        """
        if "/channel/" in url:  # Channel ID is already on URL, just parse it
            parts = urlparse(url).path.split("/")
            return parts[parts.index("channel") + 1]

        response = self.session.get(url, headers={"User-Agent": "Mozilla/4", "Accept-Language": "en-US,en;q=0.5"})
        # TODO: (may be needed) use the code below to detect consent popup and submit (GDPR countries)
        # if "<tp-yt-paper-dialog" in response.text:
        #     from lxml.html import document_fromstring  # TODO: avoid one more dependency
        #     tree = document_fromstring(response.text)
        #     form = tree.xpath("//form[contains(@action, 'consent')][1]")[0]
        #     values = {}
        #     for element in form.xpath(".//input"):
        #         elem_type = element.xpath(".//@type")
        #         if elem_type and elem_type[0] == "submit":
        #             continue
        #         name, value = element.xpath(".//@name")[0], element.xpath(".//@value")[0]
        #         values[name] = value
        #     action = form.xpath("./@action")[0]
        #     post_response = self.session.post(urljoin(response.request.url, action) data=values)

        if '<link rel="canonical" href="https://www.youtube.com/channel/' in response.text:
            return response.text.split('<link rel="canonical" href="https://www.youtube.com/channel/')[1].split('">')[0]
        result = REGEXP_CHANNEL_ID.findall(response.text)
        return result[0] if result else None

    def channel_id_from_username(self, username: str):
        """Uses Channel's API `forUsername` parameter to get channel ID (old YouTube usernames)
        This won't work for `https://youtube.com/c/username` or `https://youtube.com/@username` usernames (just for old
        usernames). If you need to find the channel ID from these formats, use the `channel_id_from_url` method.
        """
        data = self.request("channels", params={"part": "id", "forUsername": username})
        items = data.get("items", [])
        return items[0]["id"] if items else None

    def categories(self, region_code):
        response = self.request("videoCategories", params={"regionCode": region_code})
        return [parse_category_data(category) for category in response["items"]]

    def most_popular(self, region_code=None, category_id=None):
        params = {"part": "contentDetails,statistics,liveStreamingDetails,snippet,status", "chart": "mostPopular"}
        if category_id is not None:
            params["videoCategoryId"] = category_id
        if region_code is not None:
            params["regionCode"] = region_code

        for item in self.paginate("videos", params=params):
            yield parse_video_data(item)

    def channels_infos(self, channels_ids: List[str]):
        base_params = {"part": "snippet,contentDetails,statistics"}
        for batch in ipartition(channels_ids, 50):
            data = self.request("channels", params={**base_params, "id": ",".join(batch)})
            if not isinstance(data, dict) or not data.get("items"):
                continue
            result = {}
            for item in data["items"]:
                channel_info = parse_channel_data(item)
                result[channel_info["id"]] = channel_info
            for channel_id in batch:
                yield result.get(channel_id)

    def channel_playlists(self, channel_id: str):
        params = {"part": "contentDetails,snippet", "channelId": channel_id}
        for item in self.paginate("playlists", params):
            yield parse_playlist_data(item)

    def playlist_videos(self, playlist_id: str):
        """Get list of videos from a playlist (not all video parameters will be filled, check `parse_video_data`)"""
        params = {"part": "contentDetails,snippet,status", "playlistId": playlist_id}
        # TODO: should add `order`?
        for item in self.paginate("playlistItems", params):
            yield parse_video_data(item)

    def videos_infos(self, videos_ids: List[str]):
        """Retrieve information about videos in `videos_ids` list"""
        base_params = {"part": "contentDetails,statistics,liveStreamingDetails,snippet,status"}
        for batch in ipartition(videos_ids, 50):
            data = self.request("videos", params={**base_params, "id": ",".join(batch)})
            for item in data["items"]:
                yield parse_video_data(item)

    def video_comments(self, video_id: str):
        """Retrieve comments/replies for a video"""
        for item in self.paginate("commentThreads", params={"part": "id,replies,snippet", "videoId": video_id}):
            yield parse_comment_data(item["snippet"]["topLevelComment"], replies=item["snippet"]["totalReplyCount"])
            replies = item.get("replies", {}).get("comments", [])
            for reply in replies:
                yield parse_comment_data(reply)

    def video_livechat(self, video_id: str, expand_emojis=True):
        from chat_downloader import ChatDownloader
        from chat_downloader.errors import ChatDisabled, LoginRequired, NoChatReplay

        downloader = ChatDownloader()
        video_url = f"https://youtube.com/watch?v={video_id}"
        try:
            live = downloader.get_chat(video_url, message_groups=["messages", "superchat"])
        except (LoginRequired, NoChatReplay, ChatDisabled):
            raise

        for message in live.chat:
            text = message["message"]
            if expand_emojis:
                for emoji in message.get("emotes", []):
                    for shortcut in emoji["shortcuts"]:
                        text = text.replace(shortcut, emoji["id"])
            money = message.get("money", {}) or {}
            yield {
                "id": message["message_id"],
                "video_id": video_id,
                "created_at": parse_timestamp(message["timestamp"]),
                "type": message["message_type"],
                "action": message["action_type"],
                "video_time": float(message["time_in_seconds"]),
                "author": message["author"]["name"],
                "author_id": message["author"]["id"],
                "author_image_url": [img for img in message["author"]["images"] if img["id"] == "source"][0]["url"],
                "text": text,
                "money_currency": money.get("currency"),
                "money_amount": parse_decimal(money.get("amount")),
            }

    def _get_ydl(self, path_pattern, language_code):
        import yt_dlp

        key = (language_code, str(path_pattern))
        if key not in self._ydls:
            options = {
                "cachedir": False,
                "noprogress": True,
                "outtmpl": str(path_pattern),
                "quiet": True,
                "skip_download": True,
                "subtitleslangs": [language_code],
                "writeautomaticsub": True,
            }
            if self.disable_ipv6:
                options["source_address"] = "0.0.0.0"
            self._ydls[key] = yt_dlp.YoutubeDL(options)
        return self._ydls[key]

    def videos_transcriptions(self, videos_ids, language_code, path, skip_downloaded=True, batch_size=10):
        """Download video transcriptions (automatically generated) using yt-dlp"""
        # TODO: add a callback for stats?
        language_code = language_code.lower()
        path_pattern = Path(path).absolute() / "%(id)s"
        ydl = self._get_ydl(path_pattern, language_code)
        batch = []
        for video_id in videos_ids:
            filename = str(path_pattern).replace("%(id)s", f"{video_id}.{language_code}.vtt")
            if skip_downloaded and Path(filename).exists():
                continue
            batch.append(f"https://www.youtube.com/watch?v={video_id}")
            if len(batch) == batch_size:
                try:
                    ydl.download(batch)
                except Exception:
                    pass
                batch = []
        if batch:
            try:
                ydl.download(batch)
            except Exception:
                pass

    def video_search(
        self,
        term=None,
        region_code=None,
        language_code=None,
        since=None,
        until=None,
        order="date",
        channel_id=None,
        channel_type=None,
        event_type=None,
        topic=None,
        video_type=None,
        location=None,
        location_radius=None,
        safe_search=None,
        video_caption=None,
        video_definition=None,
        video_dimension=None,
        video_embeddable=None,
        video_paid_product_placement=None,
        video_syndicated=None,
        video_license=None,
        video_category_id=None,
    ):
        """Get list of videos from a search (not all video parameters will be filled, check `parse_video_data`)"""
        # https://developers.google.com/youtube/v3/docs/search/list
        # TODO: add option to search for: video, channel, playlist or everything
        params = {
            "type": "video",
            "part": "snippet",  # TODO: check if we can add more details
            "order": order,
        }
        term = str(term or "").strip()
        if term:
            params["q"] = term
        if region_code is not None:  # ISO 3166-1 alpha-2 region code
            params["regionCode"] = region_code
        if language_code is not None:  # ISO 639-1 language code
            params["relevanceLanguage"] = language_code
        if since is not None:
            params["publishedAfter"] = str(since)  # TODO: parse/check?
        if until is not None:
            params["publishedBefore"] = str(until)  # TODO: parse/check?
        if order not in ("date", "rating", "relevance", "title", "videoCount", "viewCount"):
            raise ValueError(f"Unknown order type: {repr(order)}")
        if channel_id is not None:
            params["channelId"] = channel_id
        if channel_type is not None:
            if channel_type not in ("any", "show"):
                raise ValueError("channel_type must be one of: any, show")
            params["channelType"] = channel_type
        if event_type is not None:
            if channel_type is None:
                raise ValueError("channel_type must be specified if event_type is provided")
            elif event_type not in ("completed", "live", "upcoming"):
                raise ValueError("channel_type must be one of: any, show")
            params["eventType"] = event_type
        if topic is not None:
            if topic not in self.search_topics:
                raise ValueError(
                    f"Unknown topic {repr(topic)} -- see the list at `YouTube.search_topics` or in YouTube Data API v3 docs"
                )
            params["topicId"] = self.search_topics[topic]
        if video_type is not None:
            if video_type not in ("any", "movie", "episode"):
                raise ValueError("video_type must be one of: any, movie, episode")
            params["videoType"] = video_type
        if location is not None or location_radius is not None:
            if None in (location, location_radius):
                raise ValueError("Both `location` and `location_radius` must be specified")
            elif (
                not isinstance(location, (tuple, list))
                or len(location) != 2
                or not isinstance(location[0], float)
                or not isinstance(location[1], float)
            ):
                raise ValueError("`location` must be a 2-float tuple/list")
            elif not REGEXP_LOCATION_RADIUS.match(location_radius):
                raise ValueError(
                    "`location_radius` must be string with float followed by the measurement unit: m, km, ft or mi, like in '1.2km'."
                )
            params["location"], params["locationRadius"] = ",".join(str(item) for item in location), location_radius
        if safe_search is not None:
            if safe_search not in ("moderate", "none", "strict"):
                raise ValueError("safe_search must be one of: moderate, none, strict")
            params["safeSearch"] = safe_search
        if video_caption is not None:
            if video_caption not in ("any", "closedCaption", "none"):
                raise ValueError("video_caption must be one of: any, closedCaption, none")
            params["videoCaption"] = video_caption
        if video_definition is not None:
            if video_definition not in ("any", "high", "standard"):
                raise ValueError("video_definition must be one of: any, high, standard")
            params["videoDefinition"] = video_definition
        if video_dimension is not None:
            if video_dimension not in ("2d", "3d", "any"):
                raise ValueError("video_dimension must be one of: 2d, 3d, any")
            params["videoDimension"] = video_dimension
        if video_embeddable is not None:
            if video_embeddable not in ("any", "true"):
                raise ValueError("video_embeddable must be one of: any, true")
            params["videoEmbeddable"] = video_embeddable
        if video_paid_product_placement is not None:
            if video_paid_product_placement not in ("any", "true"):
                raise ValueError("video_paid_product_placement must be one of: any, true")
            params["videoPaidProductPlacement"] = video_paid_product_placement
        if video_syndicated is not None:
            if video_syndicated not in ("any", "true"):
                raise ValueError("video_syndicated must be one of: any, true")
            params["videoSyndicated"] = video_syndicated
        if video_license is not None:
            if video_license not in ("any", "creativeCommons", "youtube"):
                raise ValueError("video_license must be one of: any, creativeCommons, youtube")
            params["videoLicense"] = video_license
        if video_category_id is not None:
            # TODO: requires `type` to be video, so we should add a validation if we transform this method in a general
            # search (not only video search)
            params["videoCategoryId"] = video_category_id

        for item in self.paginate("search", params=params):
            yield parse_video_data(item)
