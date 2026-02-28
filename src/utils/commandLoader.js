import { readdirSync, statSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { Collection } from 'discord.js';

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

export async function loadCommands() {
  const commands = new Collection();
  const commandsPath = join(__dirname, '../commands');
  const commandFiles = getCommandFiles(commandsPath);

  for (const filePath of commandFiles) {
    const command = (await import(`file://${filePath}`)).default;
    
    if ('data' in command && 'execute' in command) {
      commands.set(command.data.name, command);
      console.log(`✅ Command Found: ${command.data.name}`);
    } else {
      console.log(`⚠️ Command in ${filePath} does not have "data" or "execute"`);
    }
  }

  return commands;
}
