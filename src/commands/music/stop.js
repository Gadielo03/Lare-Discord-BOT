import { SlashCommandBuilder } from 'discord.js';
import { useQueue } from 'discord-player';

export default {
  data: new SlashCommandBuilder()
    .setName('stop_music')
    .setDescription('Stops the music and leaves the voice channel.'),
  
  async execute(interaction) {
    const queue = useQueue(interaction.guild.id);
    
    if (!queue) {
      return await interaction.reply('❌ I am not playing any music!');
    }

    queue.delete();
    await interaction.reply('⏹️ Music stopped and disconnected from the voice channel');
  }
};
