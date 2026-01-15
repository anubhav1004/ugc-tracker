import React from 'react';
import { Eye, Heart, MessageCircle, Share2, Music, ExternalLink } from 'lucide-react';

function VideoCard({ video }) {
  const formatNumber = (num) => {
    if (!num) return '0';
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  const getPlatformColor = (platform) => {
    switch (platform) {
      case 'tiktok':
        return 'bg-black';
      case 'youtube':
        return 'bg-red-600';
      case 'instagram':
        return 'bg-pink-600';
      default:
        return 'bg-gray-600';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow overflow-hidden">
      {/* Thumbnail */}
      <div className="relative aspect-video bg-gray-200">
        {video.thumbnail ? (
          <img
            src={video.thumbnail}
            alt={video.caption || 'Video'}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <Music className="w-12 h-12 text-gray-400" />
          </div>
        )}

        {/* Platform Badge */}
        <div className={`absolute top-2 right-2 ${getPlatformColor(video.platform)} text-white px-2 py-1 rounded text-xs font-semibold uppercase`}>
          {video.platform}
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Caption */}
        <p className="text-sm text-gray-900 line-clamp-2 mb-3">
          {video.caption || 'No caption'}
        </p>

        {/* Author */}
        <div className="flex items-center gap-2 mb-3">
          {video.author_avatar && (
            <img
              src={video.author_avatar}
              alt={video.author_username}
              className="w-6 h-6 rounded-full"
            />
          )}
          <span className="text-sm font-medium text-gray-700">
            @{video.author_username || 'unknown'}
          </span>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-2 mb-3">
          <div className="flex items-center gap-1 text-xs text-gray-600">
            <Eye className="w-4 h-4" />
            <span>{formatNumber(video.views)}</span>
          </div>
          <div className="flex items-center gap-1 text-xs text-gray-600">
            <Heart className="w-4 h-4" />
            <span>{formatNumber(video.likes)}</span>
          </div>
          <div className="flex items-center gap-1 text-xs text-gray-600">
            <MessageCircle className="w-4 h-4" />
            <span>{formatNumber(video.comments)}</span>
          </div>
          <div className="flex items-center gap-1 text-xs text-gray-600">
            <Share2 className="w-4 h-4" />
            <span>{formatNumber(video.shares)}</span>
          </div>
        </div>

        {/* Music */}
        {video.music_title && (
          <div className="flex items-center gap-1 text-xs text-gray-500 mb-3">
            <Music className="w-3 h-3" />
            <span className="line-clamp-1">{video.music_title}</span>
          </div>
        )}

        {/* Hashtags */}
        {video.hashtags && video.hashtags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {video.hashtags.slice(0, 3).map((hashtag, index) => (
              <span
                key={index}
                className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded"
              >
                #{hashtag}
              </span>
            ))}
            {video.hashtags.length > 3 && (
              <span className="text-xs text-gray-500">
                +{video.hashtags.length - 3} more
              </span>
            )}
          </div>
        )}

        {/* View Button */}
        {video.url && (
          <a
            href={video.url}
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full text-center py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
          >
            View Video
            <ExternalLink className="w-4 h-4" />
          </a>
        )}
      </div>
    </div>
  );
}

export default VideoCard;
