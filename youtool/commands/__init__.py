from .channel_id import ChannelId
from .channel_info import ChannelInfo
from .video_info import VideoInfo


COMMANDS = [
    ChannelId,
    ChannelInfo,
    VideoInfo
]

__all__ = [
    COMMANDS, ChannelId, ChannelInfo, VideoInfo
]