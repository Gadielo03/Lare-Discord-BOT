import { SlashCommandBuilder } from "discord.js";

export default {
  data: new SlashCommandBuilder()
    .setName('play_music')
    .setDescription('Plays music from YouTube')
    .addStringOption(option =>
      option.setName('query')
        .setDescription('YouTube URL or search query')
        .setRequired(true)
    ),
  
  async execute(interaction) {
    const voiceChannel = interaction.member.voice.channel;
    if (!voiceChannel) {
      return await interaction.reply('❌ You need to be in a voice channel to play music!');
    }

    await interaction.deferReply();

    try {
      const query = interaction.options.getString('query');
      console.log(`[PLAY] Query received: "${query}"`);

      const player = interaction.client.player;

      // Search directly on YouTube
      console.log(`[PLAY] Starting YouTube search...`);
      
      const searchQuery = query.startsWith('http') ? query : query;
      
      const searchResult = await player.search(searchQuery, {
        requestedBy: interaction.user,
        searchEngine: 'youtubeSearch'
      });

      console.log(`[PLAY] Search result:`, {
        hasResult: !!searchResult,
        hasTracks: !!searchResult?.tracks,
        tracksLength: searchResult?.tracks?.length,
        playlist: !!searchResult?.playlist
      });

      if (!searchResult || !searchResult.tracks.length) {
        return await interaction.editReply(`❌ No results found for: "${query}"`);
      }

      console.log(`[PLAY] Found: ${searchResult.tracks[0].title}`);

      // Create/get queue
      const queue = player.nodes.create(interaction.guild, {
        metadata: {
          channel: interaction.channel,
          client: interaction.guild.members.me,
          requestedBy: interaction.user
        },
        leaveOnEmptyCooldown: 300000,
        leaveOnEmpty: false,
        leaveOnEnd: false,
        selfDeaf: true,
      });

      console.log(`[PLAY] Queue created/obtained`);

      // Connect to voice channel if not connected
      try {
        if (!queue.connection) {
          console.log(`[PLAY] Connecting to voice channel...`);
          await queue.connect(voiceChannel);
          console.log(`[PLAY] Connected successfully`);
        }
      } catch (error) {
        console.error(`[PLAY] Connection error:`, error);
        queue.delete();
        return await interaction.editReply('❌ Could not join the voice channel!');
      }

      // Add track to queue
      console.log(`[PLAY] Adding track to queue...`);
      queue.addTrack(searchResult.tracks[0]);
      
      // Start playing if not already playing
      if (!queue.isPlaying()) {
        console.log(`[PLAY] Starting playback...`);
        await queue.node.play();
        console.log(`[PLAY] Playback started`);
      }

      await interaction.editReply(`🎵 Now playing: **${searchResult.tracks[0].title}**`);

    } catch (error) {
      console.error('[PLAY] Error:', error);
      await interaction.editReply('❌ Error playing music');
    }
  }
};
