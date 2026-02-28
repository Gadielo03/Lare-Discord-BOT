import 'dotenv/config';
import { REST, Routes } from 'discord.js';
import { readdirSync, statSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

function getCommandFiles(dir) {
  const files = [];
  const items = readdirSync(dir);

  for (const item of items) {
    const itemPath = join(dir, item);
    const stat = statSync(itemPath);

    if (stat.isDirectory()) {
      files.push(...getCommandFiles(itemPath));
    } else if (item.endsWith('.js')) {
      files.push(itemPath);
    }
  }

  return files;
}

const commands = [];
const commandsPath = join(__dirname, '../commands');
const commandFiles = getCommandFiles(commandsPath);

for (const filePath of commandFiles) {
  const command = (await import(`file://${filePath}`)).default;
  if ('data' in command) {
    commands.push(command.data.toJSON());
  }
}

const rest = new REST().setToken(process.env.TOKEN);

(async () => {
  try {
    console.log(`Loading ${commands.length} Commands...`);

    const guildId = process.env.GUILD_ID || '778083467438850048';
    const data = await rest.put(
      Routes.applicationGuildCommands(process.env.CLIENT_ID, guildId),
      { body: commands }
    );

    console.log(`✅ ${data.length} Commands loaded successfully in guild ${guildId}!`);
  } catch (error) {
    console.error(error);
  }
})();
