/**
 * BLAI v2 — WhatsApp Handler
 * Uses baileys (same library OpenClaw uses internally)
 * Receives messages → calls Python brain → sends reply
 */

const { default: makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const { Boom } = require('@hapi/boom');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const pino = require('pino');
const qrcode = require('qrcode-terminal');

const AUTH_DIR = path.join(__dirname, '..', 'auth');
const BRAIN_SCRIPT = path.join(__dirname, 'bridge.py');

// Track message IDs we sent (to avoid replying to our own replies in self-chat)
const sentMessageIds = new Set();

// Allowed numbers (anyone can message, but these get full access)
const ALLOWED = new Set([
  '212641503230',   // Boss (Abdul)
  '923324577459',   // Brother/Wife
  '14373310603',    // Team
  '212689063416',   // Team
]);

function normalizePhone(jid) {
  return jid.replace('@s.whatsapp.net', '').replace('@g.us', '').replace('+', '');
}

async function callBrain(phone, message, imagePath = null) {
  return new Promise((resolve, reject) => {
    const args = [
      BRAIN_SCRIPT,
      '--phone', phone,
      '--message', Buffer.from(message).toString('base64'),
    ];
    if (imagePath) {
      args.push('--image', imagePath);
    }

    const proc = exec(
      `python3 ${args.map(a => `"${a}"`).join(' ')}`,
      { timeout: 60000, maxBuffer: 1024 * 1024 },
      (error, stdout, stderr) => {
        if (error) {
          console.error('[Brain] Error:', stderr || error.message);
          resolve(null); // Don't crash on brain errors
        } else {
          resolve(stdout.trim());
        }
      }
    );
  });
}

async function startBot() {
  const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
  const { version } = await fetchLatestBaileysVersion();

  const sock = makeWASocket({
    version,
    auth: state,
    logger: pino({ level: 'silent' }),
    browser: ['BLAI', 'Chrome', '120.0'],
    connectTimeoutMs: 60000,
    defaultQueryTimeoutMs: 60000,
    getMessage: async () => undefined,
  });

  sock.ev.on('creds.update', saveCreds);

  sock.ev.on('connection.update', (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      console.log('');
      console.log('========== SCAN THIS QR CODE ==========');
      qrcode.generate(qr, { small: true });
      console.log('=======================================');
      console.log('WhatsApp > Linked Devices > Link a Device > Scan QR');
      console.log('');
    }

    if (connection === 'close') {
      const reason = new Boom(lastDisconnect?.error)?.output?.statusCode;
      console.log('[BLAI] Disconnected, reason:', reason);

      if (reason === DisconnectReason.loggedOut) {
        console.log('[BLAI] Logged out — delete auth/ folder and restart to re-scan QR');
      } else {
        // Auto-reconnect
        console.log('[BLAI] Reconnecting in 5s...');
        setTimeout(startBot, 5000);
      }
    }

    if (connection === 'open') {
      console.log('[BLAI] WhatsApp connected! Listening for messages...');
    }
  });

  sock.ev.on('messages.upsert', async ({ messages, type }) => {
    if (type !== 'notify') return;

    for (const msg of messages) {
      // Skip status updates
      if (msg.key.remoteJid === 'status@broadcast') continue;

      // BOSS PHONE NUMBER
      const BOSS_PHONE = '212641503230';
      const isSelfChat = msg.key.remoteJid === BOSS_PHONE + '@s.whatsapp.net' && msg.key.fromMe !== false;

      // RULE 1: Self-chat ("Message yourself") — only respond to Boss
      if (msg.key.fromMe) {
        // Only process self-chat messages (Boss talking to himself = talking to BLAI)
        if (!msg.key.remoteJid.includes(BOSS_PHONE)) continue;
        // Skip messages we sent as replies
        if (sentMessageIds.has(msg.key.id)) continue;
      }

      // RULE 2: Other people's chat windows — only respond if they say HI/HI BLAI
      if (!msg.key.fromMe) {
        // This is someone else messaging Boss's number
        const phone = normalizePhone(msg.key.remoteJid);

        // Extract text first to check greeting
        let previewText = '';
        if (msg.message?.conversation) previewText = msg.message.conversation;
        else if (msg.message?.extendedTextMessage?.text) previewText = msg.message.extendedTextMessage.text;

        const textLower = previewText.toLowerCase().trim();
        const isGreeting = textLower === 'hi' || textLower === 'hello' || textLower === 'hey' ||
                          textLower.startsWith('hi blai') || textLower.startsWith('hello blai') ||
                          textLower.startsWith('hey blai') || textLower === 'blai' ||
                          textLower.startsWith('hi bali') || textLower.startsWith('assalam');

        // If it's NOT a greeting, skip — don't respond in their chat window
        if (!isGreeting) {
          console.log(`[BLAI] Skipping message from +${phone} (no greeting): ${previewText.substring(0, 30)}`);
          continue;
        }
      }

      const phone = normalizePhone(msg.key.remoteJid);
      const isGroup = msg.key.remoteJid.endsWith('@g.us');

      // Skip group messages
      if (isGroup) continue;

      // Extract text
      let text = '';
      if (msg.message?.conversation) {
        text = msg.message.conversation;
      } else if (msg.message?.extendedTextMessage?.text) {
        text = msg.message.extendedTextMessage.text;
      } else if (msg.message?.imageMessage?.caption) {
        text = msg.message.imageMessage.caption || 'Image received';
      } else if (msg.message?.videoMessage?.caption) {
        text = msg.message.videoMessage.caption || 'Video received';
      } else if (msg.message?.audioMessage) {
        text = '[Voice message received — I cannot process audio yet]';
      }

      if (!text) continue;

      console.log(`[BLAI] Message from +${phone}: ${text.substring(0, 50)}...`);

      // Show typing indicator ("..." in chat)
      await sock.presenceSubscribe(msg.key.remoteJid);
      await sock.sendPresenceUpdate('composing', msg.key.remoteJid);

      // Handle image messages
      let imagePath = null;
      if (msg.message?.imageMessage) {
        try {
          const buffer = await sock.downloadMediaMessage(msg);
          imagePath = `/tmp/blai_img_${Date.now()}.jpg`;
          fs.writeFileSync(imagePath, buffer);
        } catch (e) {
          console.error('[BLAI] Failed to download image:', e.message);
        }
      }

      // Call brain
      const reply = await callBrain(phone, text, imagePath);

      // Clean up temp image
      if (imagePath && fs.existsSync(imagePath)) {
        fs.unlinkSync(imagePath);
      }

      // Stop typing indicator
      await sock.sendPresenceUpdate('paused', msg.key.remoteJid);

      if (reply) {
        const sent = await sock.sendMessage(msg.key.remoteJid, { text: reply });
        if (sent && sent.key && sent.key.id) {
          sentMessageIds.add(sent.key.id);
          setTimeout(() => sentMessageIds.delete(sent.key.id), 60000);
        }
        console.log(`[BLAI] Replied to +${phone}: ${reply.substring(0, 50)}...`);
      }
    }
  });

  // ── Outgoing queue processor: sends scheduled messages ──
  const QUEUE_FILE = path.join(__dirname, '..', 'memory', 'outgoing_queue.json');

  setInterval(async () => {
    try {
      if (!fs.existsSync(QUEUE_FILE)) return;
      const raw = fs.readFileSync(QUEUE_FILE, 'utf8');
      const queue = JSON.parse(raw);
      let changed = false;

      for (const msg of queue) {
        if (msg.sent) continue;
        try {
          const jid = msg.phone.replace('+', '') + '@s.whatsapp.net';
          await sock.sendMessage(jid, { text: msg.message });
          msg.sent = true;
          changed = true;
          console.log(`[BLAI] Sent scheduled message to +${msg.phone}: ${msg.message.substring(0, 50)}...`);
        } catch (e) {
          console.error(`[BLAI] Failed to send to ${msg.phone}:`, e.message);
        }
      }

      if (changed) {
        // Keep only last 50 messages, remove sent ones older than 1 hour
        const now = Date.now();
        const filtered = queue.filter(m => !m.sent || (now - new Date(m.timestamp).getTime() < 3600000));
        fs.writeFileSync(QUEUE_FILE, JSON.stringify(filtered.slice(-50), null, 2));
      }
    } catch (e) {
      // Queue file might be empty or malformed — ignore
    }
  }, 30000); // Check every 30 seconds
}

console.log('[BLAI v2] Starting WhatsApp bot...');
startBot().catch(console.error);
