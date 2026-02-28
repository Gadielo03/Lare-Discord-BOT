"""YouTube Service - Handles YouTube video information extraction"""
import yt_dlp
from logger import log


class YouTubeService:
    """Service for extracting YouTube video information"""
    
    @staticmethod
    def get_ydl_options(is_playlist=False):
        """Get yt-dlp options"""
        if is_playlist:
            return {
                'format': 'bestaudio',
                'noplaylist': False,
                'playlistend': 10,
                'quiet': True,
                'extract_flat': True
            }
        else:
            return {
                'format': 'bestaudio',
                'noplaylist': True,
                'quiet': True
            }
    
    @staticmethod
    def extract_song_info(url, title, info):
        """Extract relevant song information from yt-dlp result"""
        return {
            'url': url,
            'title': title,
            'thumbnail': info.get('thumbnail'),
            'duration': info.get('duration'),
            'uploader': info.get('uploader')
        }
    
    @staticmethod
    async def search_song(query):
        """Search for a single song"""
        try:
            ydl_opts = YouTubeService.get_ydl_options()
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if query.startswith("http"):
                    info = ydl.extract_info(query, download=False)
                    return YouTubeService.extract_song_info(
                        info['url'],
                        info['title'],
                        info
                    )
                else:
                    info = ydl.extract_info(f"ytsearch:{query}", download=False)
                    entry = info['entries'][0]
                    return YouTubeService.extract_song_info(
                        entry['url'],
                        entry['title'],
                        entry
                    )
        except Exception as e:
            log.error(f'Error searching song: {e}')
            raise
    
    @staticmethod
    async def process_playlist(url):
        """Process a YouTube playlist and return list of songs"""
        try:
            songs = []
            ydl_opts = YouTubeService.get_ydl_options(is_playlist=True)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:
                    for entry in info['entries'][:10]:
                        if entry:
                            ydl_single = {'format': 'bestaudio', 'quiet': True}
                            with yt_dlp.YoutubeDL(ydl_single) as ydl2:
                                song_info = ydl2.extract_info(
                                    f"https://www.youtube.com/watch?v={entry['id']}",
                                    download=False
                                )
                                songs.append(YouTubeService.extract_song_info(
                                    song_info['url'],
                                    entry['title'],
                                    song_info
                                ))
            
            return songs
        except Exception as e:
            log.error(f'Error processing playlist: {e}')
            raise
    
    @staticmethod
    def is_playlist(url):
        """Check if the URL is a playlist"""
        return 'playlist' in url.lower() or 'list=' in url
    
    @staticmethod
    async def generate_playlist_by_genre(genre, count=10):
        """Generate a playlist based on music genre or topic"""
        try:
            songs = []
            titles_seen = set()
            
            search_query = f"{genre} song -mix -compilation -hour -hours -playlist"
            
            ydl_opts = {
                'format': 'bestaudio',
                'noplaylist': True,
                'quiet': True,
                'extract_flat': False,  # Get full info to filter by duration
            }
            
            log.info(f'Searching for {count} {genre} songs...')
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch{count * 3}:{search_query}", download=False)
                
                if 'entries' in info and info['entries']:
                    for entry in info['entries']:
                        if not entry:
                            continue
                        
                        duration = entry.get('duration', 0)
                        title = entry.get('title', '')
                        
                        if title in titles_seen:
                            continue
                        
                        if duration > 600:
                            log.debug(f'Skipping long video: {title} ({duration}s)')
                            continue
                        
                        skip_keywords = ['mix', 'compilation', 'playlist', 'hour', 'hours', 'full album']
                        if any(keyword in title.lower() for keyword in skip_keywords):
                            log.debug(f'Skipping compilation: {title}')
                            continue
                        
                        songs.append(YouTubeService.extract_song_info(
                            entry['url'],
                            title,
                            entry
                        ))
                        titles_seen.add(title)
                        
                        if len(songs) >= count:
                            break
            
            log.success(f'Generated {len(songs)} songs for genre: {genre}')
            return songs[:count]
            
        except Exception as e:
            log.error(f'Error generating playlist for genre {genre}: {e}')
            raise
