# SPDX-License-Identifier: AGPL-3.0-or-later
"""Peertube and :py:obj:`SepiaSearch <searx.engines.sepiasearch>` do share
(more or less) the same REST API and the schema of the JSON result is identical.

"""

import re
from urllib.parse import urlencode
from datetime import datetime, timedelta
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

import babel

from searx.network import get  # see https://github.com/searxng/searxng/issues/762
from searx.locales import language_tag
from searx.utils import html_to_text, humanize_number
from searx.enginelib.traits import EngineTraits

traits: EngineTraits

about = {
    # pylint: disable=line-too-long
    "website": 'https://www.tubearchivist.com',
    "official_api_documentation": 'https://github.com/tubearchivist/tubearchivist',
    "use_official_api": True,
    "require_api_key": False,
    "results": 'JSON',
}

# engine dependent config
categories = ["videos"]
paging = True
base_url = ""
"""Base URL of the Tube Archivist instance.  Fill this in with your own tubearchivist url
"""
token = ""
"""Token for API use
"""


def request(query, params):
    """Assemble request for the Tubearchivist API"""

    if not query:
        return False

    params['url'] = (
        base_url.rstrip("/")
        + "/api/search?"
        + urlencode(
            {
                'query': query,
            }
        )
    )
    params['headers']['Authorization'] = f'Token {token}'

    return params


def response(resp):
    return video_response(resp)


def video_response(resp):
    """Parse video response from Tubearchivist instances."""
    results = []

    json_data = resp.json()

    if 'results' not in json_data:
        return []

    for channel_result in json_data['results']['channel_results']:
        metadata = []
        channel_url = absolute_url(f'/channel/{channel_result["channel_id"]}')
        results.append({
            'url': channel_url,
            'title': channel_result['channel_name'],
            'content': html_to_text(channel_result['channel_description']),
            'author': channel_result['channel_name'],
            'views': humanize_number(channel_result['channel_subs']),
            # 'template': 'videos.html',
            # 'publishedDate': parse(video_result['published']),
            'thumbnail': f'{absolute_url(channel_result["channel_thumb_url"])}?auth={token}',
            'metadata': ' | '.join(metadata)
        })


    for video_result in json_data['results']['video_results']:
        metadata = [
            x
            for x in [
                video_result['channel']['channel_name'],
                ' | '.join(video_result['tags']),
            ]
            if x
        ]
        results.append({
            'url': f'{base_url.rstrip("/")}{video_result["media_url"]}',
            'title': video_result['title'],
            'content': html_to_text(video_result['description']),
            'author': video_result['channel']['channel_name'],
            'length': video_result['player']['duration_str'],
            'views': humanize_number(video_result['stats']['view_count']),
            'template': 'videos.html',
            'publishedDate': parse(video_result['published']),
            'thumbnail': f'{absolute_url(video_result["vid_thumb_url"])}?auth={token}',
            'metadata': ' | '.join(metadata)
        })

    return results

def absolute_url(relative_url):

    url=f'{base_url.rstrip("/")}{relative_url}'
    print(url)
    return url

