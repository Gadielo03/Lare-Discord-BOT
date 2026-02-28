import { SlashCommandBuilder } from 'discord.js';

export default {
  data: new SlashCommandBuilder()
    .setName('info')
    .setDescription('Provides information about the server.'),
  
  async execute(interaction) {
    await interaction.reply(`Servidor: ${interaction.guild.name}\nMiembros: ${interaction.guild.memberCount}`);
  }
};
