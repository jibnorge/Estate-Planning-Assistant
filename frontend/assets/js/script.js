// ═══════════════════════════════════════════════════════════
// CLIENT DATA
// Paste your full clients.json content into this variable
// ═══════════════════════════════════════════════════════════

let CLIENTS_DATA = null;

async function loadClientsJSON() {
  const [clientsRes, findingsRes] = await Promise.all([
    fetch('../backend/config/clients.json'),
    fetch('../docs/findings.json')
  ]);

  CLIENTS_DATA = await clientsRes.json();
  FINDINGS_DATA = await findingsRes.json();

  loadClient(activeClientIndex);
}


// ═══════════════════════════════════════════════════════════
// STATE
// ═══════════════════════════════════════════════════════════

let activeClientIndex   = 1;
let activeClient        = null;
let clientFindings      = [];
let conversationHistory = [];
let FINDINGS_DATA       = null; 
let API_KEY             = null;


// ═══════════════════════════════════════════════════════════
// UTILITY — SAFE NESTED ACCESS
// ═══════════════════════════════════════════════════════════

function safeGet(obj, ...keys) {
  let current = obj;
  for (const key of keys) {
    if (current === null || current === undefined) return null;
    if (typeof current !== 'object') return null;
    current = current[key] !== undefined ? current[key] : null;
  }
  return current;
}

function formatBalance(n) {
  return '$' + (n || 0).toLocaleString('en-CA');
}

function getInitials(name) {
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
}


// ═══════════════════════════════════════════════════════════
// ANALYSIS ENGINE — JS port of your Python functions
// ═══════════════════════════════════════════════════════════

function analyzeEstateGaps(client) {
  const findings = [];
  const accounts = client.accounts || [];

  accounts.forEach(account => {
    if (account.type === 'TFSA') findings.push(...checkTFSA(account, client));
    if (account.type === 'RRSP') findings.push(...checkRRSP(account, client));
    if (account.type === 'RRIF') findings.push(...checkRRIF(account, client));
  });

  findings.push(...checkLifeEvents(client));
  findings.push(...checkCrossAccount(client));

  const order = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
  findings.sort((a, b) => (order[a.severity] ?? 9) - (order[b.severity] ?? 9));
  return findings;
}

function checkTFSA(account, client) {
  const f = [];
  const hasSuccessor   = safeGet(account, 'successor_holder') !== null;
  const hasBeneficiary = safeGet(account, 'beneficiary_primary') !== null;

  if (!hasSuccessor && !hasBeneficiary) {
    f.push({ severity: 'HIGH', account_id: account.account_id, account_type: 'TFSA', rule: 'T1',
      issue: 'No successor holder or beneficiary named on TFSA',
      consequence: 'Account loses tax-free status on death and enters estate — probate delays and tax on growth after death.',
      action: 'Name a successor holder if married. Name a beneficiary at minimum.' });
  }
  if (safeGet(account, 'successor_holder', 'is_currently_spouse') === false) {
    f.push({ severity: 'CRITICAL', account_id: account.account_id, account_type: 'TFSA', rule: 'T3',
      issue: 'Ex-spouse still listed as successor holder on TFSA',
      consequence: 'Ex-spouse inherits the entire TFSA tax-free immediately. Your will cannot override this.',
      action: 'Update immediately — highest priority fix.' });
  }
  if (safeGet(account, 'successor_holder', 'is_currently_alive') === false) {
    f.push({ severity: 'CRITICAL', account_id: account.account_id, account_type: 'TFSA', rule: 'T6',
      issue: 'Successor holder on TFSA is deceased',
      consequence: 'Designation has failed. Account falls to estate — probate, loss of tax-free status.',
      action: 'Name a new successor holder immediately.' });
  }
  if (safeGet(account, 'beneficiary_primary', 'is_currently_alive') === false) {
    f.push({ severity: 'CRITICAL', account_id: account.account_id, account_type: 'TFSA', rule: 'T6',
      issue: 'Primary beneficiary on TFSA is deceased',
      consequence: 'Designation has failed. Account falls to estate.',
      action: 'Update to a living person immediately.' });
  }
  return f;
}

function checkRRSP(account, client) {
  const f = [];
  const hasAnnuitant   = safeGet(account, 'successor_annuitant') !== null;
  const hasBeneficiary = safeGet(account, 'beneficiary_primary') !== null;

  if (!hasAnnuitant && !hasBeneficiary) {
    f.push({ severity: 'HIGH', account_id: account.account_id, account_type: 'RRSP', rule: 'R1',
      issue: 'No beneficiary or successor annuitant named on RRSP',
      consequence: `Full RRSP value added to income in year of death. Potential tax bill: ${formatBalance(Math.round((account.balance || 0) * 0.4))}+.`,
      action: 'Name spouse as successor annuitant. If no spouse, name a beneficiary.' });
  }
  if (safeGet(account, 'successor_annuitant', 'is_currently_spouse') === false) {
    f.push({ severity: 'CRITICAL', account_id: account.account_id, account_type: 'RRSP', rule: 'R3',
      issue: 'Ex-spouse still listed as successor annuitant on RRSP',
      consequence: 'Ex-spouse legally receives the entire RRSP. Your will cannot override it.',
      action: 'Update immediately. Highest priority fix.' });
  }
  if (safeGet(account, 'beneficiary_primary', 'is_currently_alive') === false) {
    f.push({ severity: 'CRITICAL', account_id: account.account_id, account_type: 'RRSP', rule: 'R6',
      issue: 'Primary beneficiary on RRSP is deceased',
      consequence: 'Designation failed. Full RRSP collapses into estate as taxable income.',
      action: 'Update beneficiary immediately.' });
  }
  return f;
}

function checkRRIF(account, client) {
  const f = [];

  if (safeGet(account, 'successor_annuitant', 'is_currently_alive') === false) {
    f.push({ severity: 'CRITICAL', account_id: account.account_id, account_type: 'RRIF', rule: 'R6',
      issue: 'Successor annuitant on RRIF is deceased',
      consequence: `RRIF balance of ${formatBalance(account.balance)} collapses into estate. Tax bill could reach ${formatBalance(Math.round((account.balance || 0) * 0.4))}+.`,
      action: 'Update successor annuitant immediately. Review estate liquidity.' });
  }
  if (safeGet(account, 'beneficiary_primary', 'is_currently_alive') === false) {
    f.push({ severity: 'CRITICAL', account_id: account.account_id, account_type: 'RRIF', rule: 'R6',
      issue: 'Primary beneficiary on RRIF is deceased',
      consequence: 'Designation failed. Full RRIF value enters estate as taxable income.',
      action: 'Update beneficiary immediately.' });
  }

  // Liquidity check
  const allAccounts    = client.accounts || [];
  const nonRegBalance  = allAccounts.filter(a => a.type === 'non-registered').reduce((s, a) => s + (a.balance || 0), 0);
  if ((account.balance || 0) > 100000 && nonRegBalance < (account.balance || 0) * 0.3) {
    f.push({ severity: 'HIGH', account_id: account.account_id, account_type: 'RRIF', rule: 'R7',
      issue: 'Large RRIF with insufficient liquid assets to cover estate tax bill',
      consequence: `RRIF: ${formatBalance(account.balance)}. Potential tax: ${formatBalance(Math.round((account.balance || 0) * 0.4))}+. Non-registered assets: only ${formatBalance(nonRegBalance)}.`,
      action: 'Review estate liquidity with a financial advisor. Consider life insurance.' });
  }
  return f;
}

function checkLifeEvents(client) {
  const f = [];
  const accounts = client.accounts || [];

  if (client.marital_status === 'married') {
    const spouseNamed = accounts.some(a =>
      safeGet(a, 'successor_holder', 'relationship') === 'spouse' ||
      safeGet(a, 'successor_annuitant', 'relationship') === 'spouse' ||
      safeGet(a, 'beneficiary_primary', 'relationship') === 'spouse'
    );
    if (!spouseNamed) {
      f.push({ severity: 'HIGH', account_id: null, account_type: 'ALL', rule: 'L1',
        issue: 'Recently married but spouse not named on any account',
        consequence: 'Spouse has no legal claim to any registered accounts. Marriage does not automatically update designations.',
        action: 'Review and update all account designations. Update your will.' });
    }
  }

  if (client.marital_status === 'divorced') {
    const exNamed = accounts.some(a =>
      safeGet(a, 'successor_holder', 'is_currently_spouse') === false ||
      safeGet(a, 'successor_annuitant', 'is_currently_spouse') === false ||
      safeGet(a, 'beneficiary_primary', 'is_currently_spouse') === false
    );
    if (exNamed) {
      f.push({ severity: 'CRITICAL', account_id: null, account_type: 'ALL', rule: 'L2',
        issue: 'Recently divorced but ex-spouse still named on one or more accounts',
        consequence: 'Divorce does NOT remove designations in Canada. Ex-spouse will legally inherit every account still in their name.',
        action: 'Treat this as an emergency. Update every designation today.' });
    }
  }

  if (!client.has_will) {
    f.push({ severity: 'HIGH', account_id: null, account_type: 'ALL', rule: 'L0a',
      issue: 'No will on file',
      consequence: 'Provincial intestacy laws distribute everything by formula — not your wishes. No guardian named for minor children.',
      action: 'Create a will as soon as possible.' });
  }

  return f;
}

function checkCrossAccount(client) {
  const f = [];
  const accounts = client.accounts || [];

  const hasAnyDesignation = a =>
    safeGet(a, 'successor_holder') !== null ||
    safeGet(a, 'successor_annuitant') !== null ||
    safeGet(a, 'beneficiary_primary') !== null;

  if (accounts.length > 0 && !accounts.some(hasAnyDesignation)) {
    f.push({ severity: 'CRITICAL', account_id: null, account_type: 'ALL', rule: 'C5',
      issue: 'No beneficiary named on any account — complete estate planning gap',
      consequence: 'Entire portfolio goes through probate. Maximum tax exposure on all registered accounts.',
      action: 'Start with your RRSP or RRIF — the tax consequences there are most severe.' });
  }
  return f;
}


// ═══════════════════════════════════════════════════════════
// RISK LEVEL FOR AN ACCOUNT
// ═══════════════════════════════════════════════════════════

function getAccountRisk(accountId, findings) {
  const hits = findings.filter(f => f.account_id === accountId);
  if (hits.some(f => f.severity === 'CRITICAL')) return 'critical';
  if (hits.some(f => f.severity === 'HIGH'))     return 'high';
  if (hits.some(f => f.severity === 'MEDIUM'))   return 'medium';
  if (hits.length === 0)                          return 'clean';
  return 'medium';
}


// ═══════════════════════════════════════════════════════════
// RENDER LEFT PANEL
// ═══════════════════════════════════════════════════════════

function renderAccounts(client, findings) {
  const list = document.getElementById('accountsList');
  list.innerHTML = '';

  client.accounts.forEach(account => {
    const risk            = getAccountRisk(account.account_id, findings);
    const accountFindings = findings.filter(f => f.account_id === account.account_id);
    const riskLabel       = risk === 'clean' ? 'CLEAN' : risk.toUpperCase();

    const card = document.createElement('div');
    card.className = `account-card risk-${risk}`;
    card.dataset.accountId = account.account_id;

    card.innerHTML = `
      <div class="account-card-top">
        <div class="account-type-badge">${account.type}</div>
        <div class="risk-badge ${risk}">${riskLabel}</div>
      </div>
      <div class="account-balance">
        ${formatBalance(account.balance)} <span>CAD</span>
      </div>
      ${accountFindings.length > 0 ? `
        <div class="account-issues">
          ${accountFindings.slice(0, 2).map(f => `
            <div class="account-issue-line" style="padding-left:4px; word-break:break-word; overflow-wrap:break-word;">${f.issue}</div>
          `).join('')}
        </div>
      ` : ''}
    `;
    list.appendChild(card);
  });

  const portfolioFindings = findings.filter(f => f.account_id === null);
  if (portfolioFindings.length > 0) {
    const divider = document.createElement('div');
    divider.style.cssText = `font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--text-dim); padding: 10px 4px 4px;`;
    divider.textContent = 'Portfolio-Level Risks';
    list.appendChild(divider);

    portfolioFindings.forEach(f => {
      const severity  = f.severity.toLowerCase();
      const cardColor = severity === 'critical' ? 'risk-critical' : severity === 'high' ? 'risk-high' : 'risk-medium';
      const card = document.createElement('div');
      card.className = `account-card ${cardColor}`;
      card.innerHTML = `
        <div class="account-card-top">
          <div class="account-type-badge">Portfolio</div>
          <div class="risk-badge ${severity}">${f.severity}</div>
        </div>
        <div class="account-issues" style="margin-top:0">
          <div class="account-issue-line" style="color: var(--text); padding-left:4px; word-break:break-word;">${f.issue}</div>
        </div>
      `;
      list.appendChild(card);
    });
  }

  document.getElementById('countCritical').textContent = findings.filter(f => f.severity === 'CRITICAL').length;
  document.getElementById('countHigh').textContent     = findings.filter(f => f.severity === 'HIGH').length;
  document.getElementById('countMedium').textContent   = findings.filter(f => f.severity === 'MEDIUM').length;
}


// ═══════════════════════════════════════════════════════════
// HIGHLIGHT ACCOUNT CARD
// ═══════════════════════════════════════════════════════════

function highlightAccount(accountId) {
  document.querySelectorAll('.account-card').forEach(card => {
    card.classList.remove('highlighted');
  });
  if (!accountId) return;
  const card = document.querySelector(`[data-account-id="${accountId}"]`);
  if (card) {
    card.classList.add('highlighted');
    card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}

function detectMentionedAccount(text, client) {
  for (const account of client.accounts) {
    if (text.toLowerCase().includes(account.type.toLowerCase())) {
      return account.account_id;
    }
  }
  return null;
}


// ═══════════════════════════════════════════════════════════
// RENDER MESSAGES
// ═══════════════════════════════════════════════════════════

function isHardStop(text) {
  return text.toLowerCase().includes('this is where i stop') ||
         text.toLowerCase().includes('i cannot make changes') ||
         text.toLowerCase().includes("i'm not permitted");
}

function renderMessage(role, text) {
  const area  = document.getElementById('messagesArea');
  const empty = document.getElementById('emptyState');
  if (empty) empty.remove();

  const hardStop    = role === 'assistant' && isHardStop(text);
  const avatarClass = role === 'assistant' ? 'assistant' : 'user-av';
  const avatarLabel = role === 'assistant' ? 'AI' : getInitials(activeClient.name);
  const roleLabel   = role === 'assistant' ? 'Assistant' : activeClient.name.split(' ')[0];

  const div = document.createElement('div');
  div.className = `message ${role}${hardStop ? ' hard-stop' : ''}`;
  div.innerHTML = `
    <div class="msg-avatar ${avatarClass}">${avatarLabel}</div>
    <div class="msg-body">
      <div class="msg-role">${roleLabel}</div>
      <div class="msg-bubble">
        ${hardStop ? '<div class="hard-stop-label">HARD STOP</div>' : ''}
        ${text.replace(/\n/g, '<br/>')}
      </div>
    </div>
  `;

  area.appendChild(div);
  area.scrollTop = area.scrollHeight;
}

function showTyping() {
  const area  = document.getElementById('messagesArea');
  const empty = document.getElementById('emptyState');
  if (empty) empty.remove();

  const div = document.createElement('div');
  div.className = 'typing-indicator';
  div.id = 'typingIndicator';
  div.innerHTML = `
    <div class="msg-avatar assistant">AI</div>
    <div class="typing-dots">
      <span></span><span></span><span></span>
    </div>
  `;
  area.appendChild(div);
  area.scrollTop = area.scrollHeight;
}

function hideTyping() {
  const t = document.getElementById('typingIndicator');
  if (t) t.remove();
}

// ═══════════════════════════════════════════════════════════
// STSTEM PROMPT — The basic prompt over which the AI works
// ═══════════════════════════════════════════════════════════

function buildSystemPrompt(client, findings) {
  const findingsText = findings.map(f =>
    `- [${f.severity}] Rule ${f.rule}: ${f.issue}\n  Consequence: ${f.consequence}\n  Action: ${f.action}`
  ).join('\n\n');

  return `You are an estate planning assistant for Vesta.
You help clients understand what happens to their accounts when they die
and identify gaps in their current setup.

YOUR RULES — follow absolutely:
1. NEVER execute or confirm any account changes. You are read-only.
2. NEVER give legal advice. Always say "confirm with an estate lawyer."
3. HARD STOP — if the client asks you to MAKE any change, respond with:
   "This is where I stop. [explain why] Here is what you need to do yourself: [steps]"
4. Explain everything as if the client has no financial background.
5. Be warm and human — this topic involves death and family.
6. Always surface CRITICAL findings first.
7. When referencing a specific account mention the account type clearly.
8. NEVER mention the names of any person other than the client themselves.
   Always refer to people by their relationship only — "your spouse", "your ex-spouse", "your child", "your partner", "your brother".
   Never say "Robert" or "Tom" or any other person's name.

CURRENT CLIENT PROFILE:
${JSON.stringify(client, null, 2)}

FINDINGS FROM ANALYSIS ENGINE:
${findingsText}

When the client first messages you, briefly acknowledge what you see
and ask what they would like to understand first.
Do not dump all findings at once — let the conversation guide depth.`;
}


// ═══════════════════════════════════════════════════════════
// SEND MESSAGE — API call goes here in the next step
// ═══════════════════════════════════════════════════════════

async function sendMessage() {
  const input = document.getElementById('chatInput');
  const text  = input.value.trim();
  if (!text) return;

  input.value = '';
  autoResize(input);
  document.getElementById('sendBtn').disabled = true;

  renderMessage('user', text);
  conversationHistory.push({ role: 'user', content: text });

  showTyping();

  // ── API CONNECTION GOES HERE IN NEXT STEP ──
	try {
		const response = await fetch('http://localhost:3001/api/messages', {
		  method: 'POST',
		  headers: {
			'Content-Type': 'application/json'
		  },
		  body: JSON.stringify({
			model: 'claude-haiku-4-5',
			max_tokens: 1024,
			system: buildSystemPrompt(activeClient, clientFindings),
			messages: conversationHistory
		  })
		});

		const data = await response.json();
		hideTyping();

		if (data.error) {
		  renderMessage('assistant', `Error: ${data.error.message}`);
		  document.getElementById('sendBtn').disabled = false;
		  return;
		}

		const reply = data.content[0].text;
		conversationHistory.push({ role: 'assistant', content: reply });
		renderMessage('assistant', reply);

		const mentioned = detectMentionedAccount(reply, activeClient);
		if (mentioned) highlightAccount(mentioned);

	  } catch (err) {
		hideTyping();
		renderMessage('assistant', `Connection error: ${err.message}`);
	  }

	  document.getElementById('sendBtn').disabled = false;
}

// ═══════════════════════════════════════════════════════════
// SWITCH CLIENT
// ═══════════════════════════════════════════════════════════

function switchClient() {
  activeClientIndex = parseInt(document.getElementById('clientSelect').value);
  loadClient(activeClientIndex);
}

function loadClient(index) {
  activeClient     = CLIENTS_DATA.clients[index].client;
  clientFindings   = FINDINGS_DATA[index].findings;
  conversationHistory = [];

  // Update topbar
  document.getElementById('clientInitials').textContent  = getInitials(activeClient.name);
  document.getElementById('clientNameLabel').textContent = activeClient.name;
  document.getElementById('panelSubtitle').textContent   =
    `${clientFindings.length} issue${clientFindings.length !== 1 ? 's' : ''} found`;

  // Render left panel
  renderAccounts(activeClient, clientFindings);

  // Reset chat
  document.getElementById('messagesArea').innerHTML = `
    <div class="empty-state" id="emptyState">
      <div class="empty-glyph">§</div>
      <div class="empty-text">
        Ask about your accounts<br/>
        Your estate. Your family. Your terms.
      </div>
    </div>
  `;
}


// ═══════════════════════════════════════════════════════════
// UI HELPERS
// ═══════════════════════════════════════════════════════════

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 100) + 'px';
}

function fillHint(el) {
  const input = document.getElementById('chatInput');
  input.value = el.textContent;
  input.focus();
  autoResize(input);
}


// ═══════════════════════════════════════════════════════════
// INIT — load default client on page open
// ═══════════════════════════════════════════════════════════

loadClientsJSON();
