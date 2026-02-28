export function logCommand(interaction) {
  const timestamp = new Date().toLocaleString('es-ES', { 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit' 
  });
  
  const user = `${interaction.user.tag} (${interaction.user.id})`;
  const guild = interaction.guild ? `${interaction.guild.name}` : 'DM';
  const command = `/${interaction.commandName}`;
  
  const options = interaction.options.data
    .map(opt => `${opt.name}: ${opt.value}`)
    .join(', ');
  
  const optionsText = options ? ` [${options}]` : '';
  
  console.log(`[${timestamp}] 📝 ${user} on ${guild} Executed: ${command}${optionsText}`);
}
