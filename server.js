const express = require('express');
const { Client } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

const app = express();
const client = new Client({
  puppeteer: {
    args: ['--no-sandbox'],
  },
webVersionCache: {
     type: 'remote',
     remotePath: 'https://raw.githubusercontent.com/wppconnect-team/wa-version/main/html/2.2411.0-beta.html',
}
});
client.on('qr', (qr) => {
  // Exibir o QR code no console
  qrcode.generate(qr, { small: true });
});

client.on('authenticated', (session) => {
  console.log('Cliente autenticado!');
  // Salvar a sessão se necessário
});

client.on('disconnected', (reason) => {
  console.log(`Cliente desconectado: ${reason}`);
  // Implementar lógica de reconexão aqui, se necessário
  // client.initialize();  // Descomente se quiser tentar uma reconexão imediata
});

client.on('ready', () => {
  console.log('Cliente está pronto!');
});

// Inicializar o cliente
client.initialize();

app.use(express.json());

app.post('/send-message', async (req, res) => {
  const { number, message } = req.body;

  try {
    // Enviar a mensagem
    await client.sendMessage(number, message);
    console.log(`Mensagem enviada para ${number}: ${message}`);
    
    return res.json({ success: true });
  } catch (err) {
    console.error('Erro ao enviar mensagem:', err);
    return res.json({ success: false, error: err.message });
  }
});

const PORT = 5000;

app.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});
