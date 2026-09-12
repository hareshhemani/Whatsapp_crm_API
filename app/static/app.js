let selectedContactId = null;

async function fetchContacts() {
    const res = await fetch('/contacts/');
    const contacts = await res.json();
    const list = document.getElementById('contact-list');
    list.innerHTML = '';
    
    contacts.forEach(contact => {
        const item = document.createElement('div');
        item.className = 'contact-item';
        item.innerHTML = `
            <div class="contact-avatar">${contact.name ? contact.name[0] : '#'}</div>
            <div class="contact-info">
                <div class="contact-name">${contact.name || contact.phone_number}</div>
                <div class="contact-last-msg">${contact.tags || 'No tags'}</div>
            </div>
        `;
        item.onclick = () => selectContact(contact);
        list.appendChild(item);
    });
}

async function selectContact(contact) {
    selectedContactId = contact.id;
    document.getElementById('current-contact-name').innerText = contact.name || contact.phone_number;
    document.getElementById('current-contact-status').innerText = 'online';
    document.getElementById('current-contact-avatar').innerText = contact.name ? contact.name[0] : '#';
    document.getElementById('current-contact-tags').innerText = contact.tags ? `[ ${contact.tags} ]` : '';
    document.getElementById('chat-header-actions').style.display = 'block';
    
    fetchMessages(contact.id);
}

async function fetchMessages(contactId) {
    if (!contactId) return;
    const res = await fetch(`/contacts/${contactId}/messages`);
    const messages = await res.json();
    const container = document.getElementById('messages-container');
    container.innerHTML = '';
    
    messages.forEach(msg => {
        const div = document.createElement('div');
        div.className = `message ${msg.direction}`;
        div.innerHTML = `
            <div class="message-text">${msg.body}</div>
            <div class="message-time">${new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</div>
        `;
        container.appendChild(div);
    });
    container.scrollTop = container.scrollHeight;
}

async function sendMessage() {
    const input = document.getElementById('message-input');
    const text = input.value;
    if (!text || !selectedContactId) return;

    // Get phone number from current contact (simplified)
    const contactsRes = await fetch('/contacts/');
    const contacts = await contactsRes.json();
    const contact = contacts.find(c => c.id === selectedContactId);

    const res = await fetch('/messages/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ to: contact.phone_number, text: text })
    });

    if (res.ok) {
        input.value = '';
        fetchMessages(selectedContactId);
    }
}

document.getElementById('send-btn').onclick = sendMessage;
document.getElementById('message-input').onkeypress = (e) => {
    if (e.key === 'Enter') sendMessage();
};

// Polling for new messages every 3 seconds
setInterval(() => {
    if (selectedContactId) fetchMessages(selectedContactId);
    fetchContacts();
}, 3000);

// Template Modal Logic
const modal = document.getElementById('template-modal');
const templateBtn = document.getElementById('template-btn');
const closeBtn = document.querySelector('.close-modal');
const confirmTplBtn = document.getElementById('confirm-send-template');

templateBtn.onclick = () => {
    if (!selectedContactId) {
        alert("Please select a contact first");
        return;
    }
    modal.style.display = 'flex';
};

closeBtn.onclick = () => {
    modal.style.display = 'none';
};

window.onclick = (event) => {
    if (event.target == modal) {
        modal.style.display = 'none';
    }
};

async function sendTemplate() {
    const name = document.getElementById('tpl-name').value;
    const lang = document.getElementById('tpl-lang').value;
    const varsStr = document.getElementById('tpl-vars').value;
    
    if (!name) {
        alert("Please enter template name");
        return;
    }

    const variables = varsStr ? varsStr.split(',').map(v => v.trim()) : [];

    // Get phone number
    const contactsRes = await fetch('/contacts/');
    const contacts = await contactsRes.json();
    const contact = contacts.find(c => c.id === selectedContactId);

    const payload = {
        to: contact.phone_number,
        template_name: name,
        language_code: lang,
        variables: variables
    };

    confirmTplBtn.disabled = true;
    confirmTplBtn.innerText = "Sending...";

    try {
        const res = await fetch('/api/templates/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            modal.style.display = 'none';
            fetchMessages(selectedContactId);
            // Clear inputs
            document.getElementById('tpl-name').value = '';
            document.getElementById('tpl-vars').value = '';
        } else {
            const err = await res.json();
            alert("Error: " + (err.detail || "Failed to send template"));
        }
    } catch (e) {
        alert("Network error: " + e.message);
    } finally {
        confirmTplBtn.disabled = false;
        confirmTplBtn.innerText = "Send Template";
    }
}

// CSV Import Logic
const importBtn = document.getElementById('import-contacts-btn');
const csvInput = document.getElementById('csv-file-input');

importBtn.onclick = () => csvInput.click();

csvInput.onchange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    importBtn.style.color = 'var(--primary)';
    try {
        const res = await fetch('/api/contacts/upload-csv', {
            method: 'POST',
            body: formData
        });
        const result = await res.json();
        if (res.ok) {
            alert(result.message);
            fetchContacts();
        } else {
            alert("Error: " + result.detail);
        }
    } catch (err) {
        alert("Upload failed: " + err.message);
    } finally {
        importBtn.style.color = '';
        csvInput.value = ''; // Reset input
    }
};

// Automation Rules Logic
const autoModal = document.getElementById('automation-modal');
const autoBtn = document.getElementById('automation-rules-btn');
const autoCloseBtn = document.querySelector('.close-modal-auto');
const saveRuleBtn = document.getElementById('save-rule');

autoBtn.onclick = () => {
    autoModal.style.display = 'flex';
    fetchRules();
};

autoCloseBtn.onclick = () => {
    autoModal.style.display = 'none';
};

async function fetchRules() {
    const res = await fetch('/api/automation/');
    const rules = await res.json();
    const list = document.getElementById('rules-list');
    list.innerHTML = '';
    
    if (rules.length === 0) {
        list.innerHTML = '<p style="color: #666; text-align: center;">No rules set yet.</p>';
        return;
    }

    rules.forEach(rule => {
        const div = document.createElement('div');
        div.style.padding = '10px';
        div.style.borderBottom = '1px solid #eee';
        div.innerHTML = `
            <strong>Keyword:</strong> ${rule.keyword} <br>
            <strong>Reply:</strong> ${rule.response}
        `;
        list.appendChild(div);
    });
}

async function saveRule() {
    const keyword = document.getElementById('auto-keyword').value;
    const response = document.getElementById('auto-response').value;

    if (!keyword || !response) {
        alert("Please fill both fields");
        return;
    }

    const res = await fetch('/api/automation/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyword, response })
    });

    if (res.ok) {
        document.getElementById('auto-keyword').value = '';
        document.getElementById('auto-response').value = '';
        fetchRules();
    }
}

saveRuleBtn.onclick = saveRule;

// Broadcast Logic
const bcModal = document.getElementById('broadcast-modal');
const bcBtn = document.getElementById('broadcast-btn');
const bcCloseBtn = document.querySelector('.close-modal-bc');
const confirmBcBtn = document.getElementById('confirm-broadcast');

bcBtn.onclick = () => {
    bcModal.style.display = 'flex';
};

bcCloseBtn.onclick = () => {
    bcModal.style.display = 'none';
};

async function startBroadcast() {
    const tplName = document.getElementById('bc-tpl-name').value;
    const tplLang = document.getElementById('bc-tpl-lang').value;
    const tagFilter = document.getElementById('bc-tag-filter').value;
    const progressDiv = document.getElementById('bc-progress');

    if (!tplName) {
        alert("Please enter template name");
        return;
    }

    confirmBcBtn.disabled = true;
    confirmBcBtn.innerText = "Processing...";
    progressDiv.innerText = "Starting broadcast...";

    try {
        const res = await fetch('/api/templates/broadcast', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                template_name: tplName,
                language_code: tplLang,
                tag_filter: tagFilter || null
            })
        });
        const result = await res.json();
        if (res.ok) {
            progressDiv.innerText = `Success! Sent to ${result.processed} contacts.`;
            setTimeout(() => {
                bcModal.style.display = 'none';
                progressDiv.innerText = '';
                confirmBcBtn.disabled = false;
                confirmBcBtn.innerText = "Start Broadcast";
            }, 2000);
        } else {
            alert("Error: " + result.message);
            confirmBcBtn.disabled = false;
            confirmBcBtn.innerText = "Start Broadcast";
        }
    } catch (err) {
        alert("Broadcast failed: " + err.message);
        confirmBcBtn.disabled = false;
        confirmBcBtn.innerText = "Start Broadcast";
    }
}

confirmBcBtn.onclick = startBroadcast;



// Add Single Contact Logic
const addContactModal = document.getElementById('add-contact-modal');
const addContactBtn = document.getElementById('add-contact-btn');
const addCloseBtn = document.querySelector('.close-modal-add');
const confirmAddBtn = document.getElementById('confirm-add-contact');

addContactBtn.onclick = () => {
    addContactModal.style.display = 'flex';
};

addCloseBtn.onclick = () => {
    addContactModal.style.display = 'none';
};

async function addSingleContact() {
    const phone = document.getElementById('add-phone').value;
    const name = document.getElementById('add-name').value;
    const tags = document.getElementById('add-tags').value;

    if (!phone) {
        alert("Please enter phone number");
        return;
    }

    const res = await fetch('/contacts/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            phone_number: phone,
            name: name,
            tags: tags
        })
    });

    if (res.ok) {
        addContactModal.style.display = 'none';
        document.getElementById('add-phone').value = '';
        document.getElementById('add-name').value = '';
        document.getElementById('add-tags').value = '';
        fetchContacts();
    } else {
        const err = await res.json();
        alert("Error: " + err.detail);
    }
}

confirmAddBtn.onclick = addSingleContact;

// Delete Contact Logic
document.getElementById('delete-contact-btn').onclick = async () => {
    if (!selectedContactId) return;
    if (!confirm("Are you sure you want to delete this contact?")) return;

    const res = await fetch(`/contacts/${selectedContactId}`, { method: 'DELETE' });
    if (res.ok) {
        selectedContactId = null;
        document.getElementById('current-contact-name').innerText = 'Select a contact';
        document.getElementById('current-contact-tags').innerText = '';
        document.getElementById('chat-header-actions').style.display = 'none';
        document.getElementById('messages-container').innerHTML = '';
        fetchContacts();
    }
};

// Analytics Logic
const statsModal = document.getElementById('stats-modal');
const showStatsBtn = document.getElementById('show-stats-btn');
const closeStatsBtn = document.querySelector('.close-modal-stats');

showStatsBtn.onclick = async () => {
    statsModal.style.display = 'flex';
    const res = await fetch('/api/analytics/stats');
    const data = await res.json();
    document.getElementById('stat-total-contacts').innerText = data.total_contacts;
    document.getElementById('stat-total-msgs').innerText = data.total_messages;
    document.getElementById('stat-inbound').innerText = data.inbound;
    document.getElementById('stat-outbound').innerText = data.outbound;
};

closeStatsBtn.onclick = () => statsModal.style.display = 'none';

// Media Logic (Simplified URL based)
document.querySelector('.fa-paperclip').onclick = async () => {
    if (!selectedContactId) {
        alert("Please select a contact first");
        return;
    }
    const url = prompt("Enter Image/PDF URL to send:");
    if (!url) return;

    // Get phone number
    const contactsRes = await fetch('/contacts/');
    const contacts = await contactsRes.json();
    const contact = contacts.find(c => c.id === selectedContactId);

    const res = await fetch('/messages/send-media', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            to: contact.phone_number, 
            media_url: url,
            media_type: url.toLowerCase().endsWith('.pdf') ? 'document' : 'image'
        })
    });

    if (res.ok) {
        fetchMessages(selectedContactId);
    } else {
        alert("Failed to send media");
    }
};

// Initial load
fetchContacts();
