/**
 * BLAI v2 — WhatsApp Handler (stable build v5)
 *
 * Key stability rules:
 * 1. NO internal reconnection — PM2 handles all restarts with delay
 * 2. Skip stale messages on connect (wait 5s before processing)
 * 3. Deduplicate messages across reconnects
 * 4. Delete corrupt session-*.json on Bad MAC errors
 * 5. Process messages one at a time (no parallel brain calls)
 */
const { default: makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion, downloadMediaMessage } = require('@whiskeysockets/baileys');
const { Boom } = require('@hapi/boom');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const pino = require('pino');
const qrcode = require('qrcode-terminal');

const AUTH_DIR = path.join(__dirname, '..', 'auth');
const BRAIN_SCRIPT = path.join(__dirname, 'bridge.py');
const BOSS_PHONE = '212641503230';
const BOSS_LID = '72426671055054';
const HEALTH_FILE = path.join(__dirname, '..', '.health');

const sentMessageIds = new Set();
const lastReplyTime = new Map();
const processedMsgIds = new Set();
const activeConversations = new Map();
const CONVERSATION_TIMEOUT = 5 * 60 * 1000;

let sock = null;
let ready = false;  // true after 5s stabilization window

function writeHealth(status) {
  try {
    fs.writeFileSync(HEALTH_FILE, JSON.stringify({
      status, pid: process.pid, timestamp: Date.now(), uptime: process.uptime()
    }));
  } catch(e) {}
}

function isBoss(jid) { return jid.includes(BOSS_PHONE) || jid.includes(BOSS_LID); }

function normalizePhone(jid) {
  return jid.replace('@s.whatsapp.net', '').replace('@g.us', '').replace('@lid', '').replace('+', '');
}

function isConversationActive(phone) {
  const conv = activeConversations.get(phone);
  if (!conv) return false;
  if (Date.now() - conv.lastMessage > CONVERSATION_TIMEOUT) { activeConversations.delete(phone); return false; }
  return conv.active;
}

function activateConversation(phone) { activeConversations.set(phone, { lastMessage: Date.now(), active: true }); }
function touchConversation(phone) { const c = activeConversations.get(phone); if (c && c.active) c.lastMessage = Date.now(); }

async function callBrain(phone, message, imagePath, videoPath) {
  return new Promise(function(resolve) {
    const args = [BRAIN_SCRIPT, '--phone', phone, '--message', Buffer.from(message).toString('base64')];
    if (imagePath) args.push('--image', imagePath);
    if (videoPath) args.push('--video', videoPath);
    const cmd = 'python3 ' + args.map(a => '"' + a + '"').join(' ');
    // Longer timeout when a video is being transcribed (Whisper roundtrip)
    const tmo = videoPath ? 180000 : 60000;
    exec(cmd, { timeout: tmo, maxBuffer: 4 * 1024 * 1024 }, function(error, stdout, stderr) {
      if (error) { console.error('[Brain] Error:', stderr || error.message); resolve(null); }
      else resolve(stdout.trim());
    });
  });
}

async function transcribeAudio(audioPath) {
  const pyScript = path.join(__dirname, 'transcribe_voice.py');
  return new Promise(function(resolve) {
    exec('python3 "' + pyScript + '" "' + audioPath + '"', { timeout: 45000, maxBuffer: 1024 * 1024 }, function(error, stdout, stderr) {
      if (error) { console.error('[Voice] Error:', stderr || error.message); resolve(null); }
      else resolve(stdout.trim());
    });
  });
}

async function handleMessage(msg) {
  if (!sock || !ready) return;
  if (msg.key.remoteJid === 'status@broadcast') return;
  if (msg.key.remoteJid.includes('@newsletter')) return;
  if (msg.key.remoteJid.endsWith('@g.us')) return;

  // === DEDUP: skip if already processed ===
  const msgId = msg.key.id;
  if (processedMsgIds.has(msgId)) return;
  processedMsgIds.add(msgId);
  // Keep set from growing forever
  if (processedMsgIds.size > 500) {
    const arr = Array.from(processedMsgIds);
    for (let i = 0; i < 250; i++) processedMsgIds.delete(arr[i]);
  }

  // === SKIP OLD MESSAGES (older than 30s) ===
  const msgTimestamp = (msg.messageTimestamp || 0);
  const msgAge = Date.now() / 1000 - msgTimestamp;
  if (msgAge > 30) {
    return;  // Silent skip — don't even log, saves resources
  }

  const phone = normalizePhone(msg.key.remoteJid);
  const isBossMsg = isBoss(msg.key.remoteJid);

  if (msg.key.fromMe) {
    if (!isBossMsg) return;
    if (sentMessageIds.has(msg.key.id)) return;
    const lr = lastReplyTime.get(msg.key.remoteJid);
    if (lr && Date.now() - lr < 15000) return;
  }

  if (!msg.key.fromMe && !isBossMsg) {
    const previewText = msg.message?.conversation || msg.message?.extendedTextMessage?.text || '';
    const textLower = previewText.toLowerCase().trim();
    const isGreeting = ['hi','hello','hey','blai'].includes(textLower) ||
      textLower.startsWith('hi blai') || textLower.startsWith('hello blai') ||
      textLower.startsWith('hey blai') || textLower.startsWith('hi bali') ||
      textLower.startsWith('assalam');
    if (isGreeting) {
      activateConversation(phone);
    } else if (isConversationActive(phone)) {
      touchConversation(phone);
    } else {
      return;
    }
  }

  let text = msg.message?.conversation || msg.message?.extendedTextMessage?.text ||
    msg.message?.imageMessage?.caption || msg.message?.videoMessage?.caption || '';

  if (msg.message?.audioMessage) {
    try {
      const audioBuf = await downloadMediaMessage(msg, 'buffer', {}, { logger: pino({ level: 'silent' }), reuploadRequest: sock.updateMediaMessage });
      const audioPath = '/tmp/blai_voice_' + Date.now() + '.ogg';
      fs.writeFileSync(audioPath, audioBuf);
      const transcription = await transcribeAudio(audioPath);
      if (fs.existsSync(audioPath)) fs.unlinkSync(audioPath);
      if (transcription) {
        text = isBossMsg || msg.key.fromMe
          ? '[Voice transcription]:\n' + transcription
          : transcription;
        if (!isBossMsg && !msg.key.fromMe) {
          try { await sock.sendMessage(BOSS_LID + '@lid', { text: '[Voice from +' + phone + ']:\n' + transcription }); } catch(e) {}
        }
      } else {
        text = '[Voice message - could not transcribe]';
      }
    } catch(e) {
      console.error('[BLAI] Voice error:', e.message);
      text = '[Voice message received]';
    }
  }

  // Allow video-only messages (no caption) — they still need to be transcribed
  if (!text && !msg.message?.videoMessage) return;
  if (!text && msg.message?.videoMessage) text = "[video]";

  console.log('[BLAI] Processing +' + phone + ': ' + text.substring(0, 50));
  writeHealth('processing');

  try { await sock.presenceSubscribe(msg.key.remoteJid); } catch(e) {}
  try { await sock.sendPresenceUpdate('composing', msg.key.remoteJid); } catch(e) {}

  let imagePath = null;
  if (msg.message?.imageMessage) {
    try {
      const imgBuf = await downloadMediaMessage(msg, 'buffer', {}, { logger: pino({ level: 'silent' }), reuploadRequest: sock.updateMediaMessage });
      imagePath = '/tmp/blai_img_' + Date.now() + '.jpg';
      fs.writeFileSync(imagePath, imgBuf);
    } catch(e) { console.error('[BLAI] Image error:', e.message); }
  }

  // VIDEO support — download and pass to brain so Whisper can transcribe
  let videoPath = null;
  if (msg.message?.videoMessage) {
    try {
      const vidBuf = await downloadMediaMessage(msg, 'buffer', {}, { logger: pino({ level: 'silent' }), reuploadRequest: sock.updateMediaMessage });
      videoPath = '/tmp/blai_vid_' + Date.now() + '.mp4';
      fs.writeFileSync(videoPath, vidBuf);
      console.log('[BLAI] Video downloaded:', videoPath, '(' + vidBuf.length + ' bytes)');
    } catch(e) { console.error('[BLAI] Video error:', e.message); }
  }

  let reply = await callBrain(phone, text, imagePath, videoPath);
  if (imagePath && fs.existsSync(imagePath)) fs.unlinkSync(imagePath);
  if (videoPath && fs.existsSync(videoPath)) fs.unlinkSync(videoPath);
  try { await sock.sendPresenceUpdate('paused', msg.key.remoteJid); } catch(e) {}

  // If brain returned empty (both Gemini & Groq failed), send multilingual fallback
  if (!reply || reply.trim() === '') {
    const resetTime = new Date();
    resetTime.setUTCHours(24 + 7, 0, 0, 0);
    const resetStr = resetTime.toLocaleString('en-US', { timeZone: 'Africa/Casablanca', weekday: 'short', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', hour12: true });
    reply = [
      '*BLAI - Black Layers AI*',
      '',
      'Thank you for reaching out! Our AI assistant is currently undergoing maintenance and will be back online shortly.',
      '',
      'We will be fully operational by: *' + resetStr + ' (PT)*',
      '',
      'For urgent inquiries, please contact us at:',
      'info@blacklayers.ca | blacklayers.ca',
      '',
      '---',
      '',
      'Merci de nous avoir contact\u00e9s ! Notre assistant IA est en cours de maintenance et sera de retour en ligne tr\u00e8s bient\u00f4t.',
      '',
      'Vielen Dank f\u00fcr Ihre Nachricht! Unser KI-Assistent wird in K\u00fcrze wieder verf\u00fcgbar sein.',
      '',
      '\u0622\u067E \u06A9\u06CC \u062F\u0644\u0686\u0633\u067E\u06CC \u06A9\u0627 \u0634\u06A9\u0631\u06CC\u06C1! \u06C1\u0645\u0627\u0631\u0627 AI \u0627\u0633\u0633\u0679\u0646\u0679 \u0627\u0628\u06BE\u06CC \u062F\u06CC\u06A9\u06BE \u0628\u06BE\u0627\u0644 \u0645\u06CC\u06BA \u062F\u0633\u062A\u06CC\u0627\u0628 \u06C1\u0648\u06AF\u0627\u06D4',
      '',
      '\u0634\u0643\u0631\u0627 \u0644\u062A\u0648\u0627\u0635\u0644\u0643\u0645! \u0633\u064A\u0639\u0648\u062F \u0645\u0633\u0627\u0639\u062F\u0646\u0627 \u0627\u0644\u0630\u0643\u064A \u0642\u0631\u064A\u0628\u0627\u064B.',
      '',
      '--- Black Layers ---'
    ].join('\n');
    console.log('[BLAI] Quota fallback message sent to +' + phone);
  }

  if (reply && sock) {
    try {
      const sent = await sock.sendMessage(msg.key.remoteJid, { text: reply });
      if (sent && sent.key && sent.key.id) {
        sentMessageIds.add(sent.key.id);
        setTimeout(function() { sentMessageIds.delete(sent.key.id); }, 60000);
      }
      lastReplyTime.set(msg.key.remoteJid, Date.now());
      console.log('[BLAI] Replied to +' + phone + ': ' + reply.substring(0, 50));
    } catch(e) {
      console.error('[BLAI] Send failed:', e.message);
    }
  }
}

async function main() {
  if (!fs.existsSync(AUTH_DIR)) fs.mkdirSync(AUTH_DIR, { recursive: true });

  const authState = await useMultiFileAuthState(AUTH_DIR);
  const versionInfo = await fetchLatestBaileysVersion();
  console.log('[BLAI] Baileys v' + versionInfo.version.join('.'));

  sock = makeWASocket({
    version: versionInfo.version,
    auth: authState.state,
    logger: pino({ level: 'silent' }),
    browser: ['BLAI', 'Safari', '18.0'],
    connectTimeoutMs: 60000,
    defaultQueryTimeoutMs: 60000,
    markOnlineOnConnect: false,
    syncFullHistory: false,
    fireInitQueries: false,
    // Auto-retry failed decrypts (fixes "Waiting for this message" Bad MAC issue)
    maxMsgRetryCount: 5,
    retryRequestDelayMs: 2000,
    // Return undefined so Baileys asks the sender to re-send the original cleartext.
    // This silently heals sessions without the user having to delete/resend.
    getMessage: async function(key) {
      console.log('[BLAI] Decrypt retry requested for', key && key.id);
      return undefined;
    },
  });

  sock.ev.on('creds.update', authState.saveCreds);

  sock.ev.on('connection.update', function(update) {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      console.log('\n========== SCAN THIS QR CODE ==========');
      qrcode.generate(qr, { small: true });
      console.log('=======================================');
      console.log('WhatsApp > Linked Devices > Link a Device > Scan QR\n');
    }

    if (connection === 'close') {
      const statusCode = new Boom(lastDisconnect?.error)?.output?.statusCode;
      console.log('[BLAI] Disconnected, reason:', statusCode);
      writeHealth('disconnected-' + statusCode);

      if (statusCode === DisconnectReason.loggedOut) {
        console.log('[BLAI] Logged out — wiping auth...');
        try { fs.rmSync(AUTH_DIR, { recursive: true, force: true }); } catch(e) {}
      }

      process.exit(1);
    }

    if (connection === 'open') {
      console.log('[BLAI] CONNECTED. Stabilizing for 5s before processing messages...');
      writeHealth('connected');

      // Wait 5 seconds before processing messages
      // This lets WhatsApp finish syncing old messages without us trying to reply
      ready = false;
      setTimeout(function() {
        ready = true;
        console.log('[BLAI] READY. Now processing messages.');
        writeHealth('ready');
      }, 5000);
    }
  });

  // Message queue — process one at a time
  const messageQueue = [];
  let processing = false;

  async function processQueue() {
    if (processing || messageQueue.length === 0) return;
    processing = true;
    const msg = messageQueue.shift();
    try { await handleMessage(msg); } catch(e) { console.error('[BLAI] Handler error:', e.message); }
    processing = false;
    if (messageQueue.length > 0) setTimeout(processQueue, 500);  // 500ms between messages
  }

  sock.ev.on('messages.upsert', function(upsert) {
    if (upsert.type !== 'notify') return;
    for (const msg of upsert.messages) {
      messageQueue.push(msg);
    }
    processQueue();
  });

  // Health heartbeat
  setInterval(function() { if (ready) writeHealth('alive'); }, 30000);

  // Outgoing queue
  const QUEUE_FILE = path.join(__dirname, '..', 'memory', 'outgoing_queue.json');
  setInterval(async function() {
    try {
      if (!sock || !ready || !fs.existsSync(QUEUE_FILE)) return;
      const queue = JSON.parse(fs.readFileSync(QUEUE_FILE, 'utf8'));
      let changed = false;
      for (const m of queue) {
        if (m.sent) continue;
        try {
          await sock.sendMessage(m.phone.replace('+', '') + '@s.whatsapp.net', { text: m.message });
          m.sent = true; changed = true;
        } catch(e) {}
      }
      if (changed) {
        const now = Date.now();
        const filtered = queue.filter(m => !m.sent || (now - new Date(m.timestamp).getTime() < 3600000));
        fs.writeFileSync(QUEUE_FILE, JSON.stringify(filtered.slice(-50), null, 2));
      }
    } catch(e) {}
  }, 30000);
}

process.on('SIGTERM', () => process.exit(0));
process.on('SIGINT', () => process.exit(0));

console.log('[BLAI v2] Starting...');
main().catch(function(e) {
  console.error('[BLAI] Fatal:', e.message);
  process.exit(1);
});
