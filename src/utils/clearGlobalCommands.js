import 'dotenv/config';
import { REST, Routes } from 'discord.js';

const rest = new REST().setToken(process.env.TOKEN);

(async () => {
  try {
    const guildId = process.env.GUILD_ID || '778083467438850048';
    
    console.log('🗑️ Erasing Guild Commands...');
    
    await rest.put(
      Routes.applicationGuildCommands(process.env.CLIENT_ID, guildId),
      { body: [] }
    );
    
    console.log('✅ Guild Commands erased successfully!');
    
    console.log('🗑️ Erasing Global Commands...');
    
    await rest.put(
      Routes.applicationCommands(process.env.CLIENT_ID),
      { body: [] }
    );
    
    console.log('✅ Global Commands erased successfully!');
  } catch (error) {
    console.error(error);
  }
})();
