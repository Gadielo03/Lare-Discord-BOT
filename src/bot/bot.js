import 'dotenv/config';
import { Client, Events, GatewayIntentBits } from 'discord.js';
import { loadCommands } from '../utils/commandLoader.js';
import { getVoiceConnections } from '@discordjs/voice';
import { logCommand } from '../utils/logger.js';
import { Player } from 'discord-player';
import { DefaultExtractors } from '@discord-player/extractor';

const client = new Client({ 
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildVoiceStates
  ] 
});

// Configurar discord-player
const player = new Player(client, {
  skipFFmpeg: false,
  ytdlOptions: {
    quality: 'highestaudio',
    highWaterMark: 1 << 25
  }
});
await player.extractors.loadMulti(DefaultExtractors);

// Event listeners para debugging
player.events.on('playerStart', (queue, track) => {
  console.log(`[PLAYER] Iniciando reproducción: ${track.title}`);
});

player.events.on('audioTrackAdd', (queue, track) => {
  console.log(`[PLAYER] Track agregado a la cola: ${track.title}`);
});

player.events.on('error', (queue, error) => {
  console.error(`[PLAYER] Error general:`, error);
});

player.events.on('playerError', (queue, error) => {
  console.error(`[PLAYER] Error de reproducción:`, error);
});

player.events.on('debug', (queue, message) => {
  console.log(`[PLAYER DEBUG] ${message}`);
});

client.player = player;

client.commands = await loadCommands();

client.on(Events.ClientReady, readyClient => {
  console.log(`Logged in as ${readyClient.user.tag}!`);
});

client.on(Events.InteractionCreate, async interaction => {
  if (!interaction.isChatInputCommand()) return;

  // Logger middleware
  logCommand(interaction);

  const command = client.commands.get(interaction.commandName);

  if (!command) {
    console.error(`Command not Found: ${interaction.commandName}`);
    return;
  }

  try {
    await command.execute(interaction);
  } catch (error) {
    console.error(error);
    if (interaction.replied || interaction.deferred) {
      await interaction.followUp({ content: '❌ Error Executing Command', ephemeral: true });
    } else {
      await interaction.reply({ content: '❌ Error Executing Command', ephemeral: true });
    }
  }
});

async function shutdown() {
  console.log('\n🔴 Shutting down bot...');
  
  const connections = getVoiceConnections();
  for (const [, connection] of connections) {
    connection.destroy();
  }
  
  await client.destroy();
  console.log('✅ Bot Desconected and Resources Cleaned Up');
  process.exit(0);
}

process.on('SIGINT', shutdown);  
process.on('SIGTERM', shutdown); 

client.login(process.env.TOKEN);
