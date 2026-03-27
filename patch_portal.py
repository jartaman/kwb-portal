import sys, re

filepath = '/Users/Danielnajman2/Downloads/kwb-portal-repo/index.html'

with open(filepath, 'r') as f:
    html = f.read()

# ── NEW handleGoogleCredential function ──────────────────────────────────────
# Logic:
#   1. POST /Login/Sign → always succeeds if Google token is valid
#   2. Store token+userId in memory
#   3. Try GET establishment → if confirmed listing found → dashboard
#   4. If no listing or unconfirmed → show Claim screen inside portal
# ─────────────────────────────────────────────────────────────────────────────

NEW_HANDLE = '''async function handleGoogleCredential(response) {
  const idToken = response.credential;
  if (!idToken) {
    showLoginError('Google sign-in failed. Please try again.');
    setGoogleBtnLoading(false);
    return;
  }
  try {
    // Step 1 — authenticate with KWB API
    const res = await kwbPost('/Login/Sign', { IdToken: idToken });
    const data = await res.json();

    if (!data || !data.DataSource || !data.DataSource.Token) {
      showLoginError('Sign-in failed. Please try again.');
      setGoogleBtnLoading(false);
      return;
    }

    // Always store the session — login itself always succeeds
    currentUser = data.DataSource;
    currentUser.idToken = idToken;

    // Step 2 — try to load their establishment
    try {
      const estRes = await kwbPost('/Place/GetEstablishment', {
        IdToken: currentUser.Token,
        Id: currentUser.Id
      });
      const estData = await estRes.json();

      if (estData && estData.DataSource && estData.DataSource.Id) {
        // Has a linked listing — go to dashboard
        loadDashboardData(estData.DataSource);
        showScreen('portal');
      } else {
        // No listing linked yet — show claim screen
        showScreen('claimScreen');
      }
    } catch(e) {
      // API error on establishment lookup → show claim screen
      showScreen('claimScreen');
    }

  } catch (err) {
    console.error('KWB login error:', err);
    showLoginError('Connection error. Please try again.');
  }
  setGoogleBtnLoading(false);
}

function showScreen(screenId) {
  document.getElementById('loginPage').style.display = 'none';
  document.getElementById('portal').style.display = 'none';
  const claim = document.getElementById('claimScreen');
  if (claim) claim.style.display = 'none';

  if (screenId === 'portal') {
    document.getElementById('portal').style.display = 'block';
  } else if (screenId === 'claimScreen') {
    if (claim) {
      claim.style.display = 'flex';
    } else {
      // claimScreen div doesn't exist yet — inject it
      injectClaimScreen();
      document.getElementById('claimScreen').style.display = 'flex';
    }
  }
}

function injectClaimScreen() {
  const div = document.createElement('div');
  div.id = 'claimScreen';
  div.style.cssText = 'display:none;position:fixed;inset:0;background:var(--bg);flex-direction:column;align-items:center;justify-content:center;z-index:100;';
  div.innerHTML = `
    <div style="background:var(--card);border-radius:16px;padding:40px;max-width:480px;width:90%;text-align:center;">
      <div style="font-size:40px;margin-bottom:16px;">🍽️</div>
      <h2 style="margin:0 0 8px;font-size:22px;">Claim Your Restaurant</h2>
      <p style="color:var(--muted);margin:0 0 24px;font-size:14px;">
        Your Google account isn't linked to a KWB listing yet.<br>
        Search for your restaurant below.
      </p>
      <input id="claimSearch" type="text" placeholder="Restaurant name or city..."
        style="width:100%;box-sizing:border-box;padding:12px 16px;border-radius:10px;border:1.5px solid var(--border);background:var(--bg);color:var(--text);font-size:15px;margin-bottom:12px;"
        oninput="searchForClaim(this.value)"
      />
      <div id="claimResults" style="text-align:left;max-height:220px;overflow-y:auto;margin-bottom:16px;"></div>
      <div id="claimStatus" style="font-size:13px;color:var(--muted);min-height:20px;"></div>
      <p style="margin:20px 0 0;font-size:13px;color:var(--muted);">
        Can't find it? <a href="https://wa.me/17866303496" target="_blank" style="color:var(--green);">WhatsApp us →</a>
      </p>
    </div>
  `;
  document.body.appendChild(div);
}

let claimSearchTimeout = null;
function searchForClaim(query) {
  clearTimeout(claimSearchTimeout);
  if (query.length < 2) {
    document.getElementById('claimResults').innerHTML = '';
    return;
  }
  claimSearchTimeout = setTimeout(async () => {
    try {
      const res = await kwbPost('/Place/SearchEstablishments', { Query: query });
      const data = await res.json();
      const results = document.getElementById('claimResults');
      if (!data || !data.DataSource || !data.DataSource.length) {
        results.innerHTML = '<p style="color:var(--muted);font-size:13px;padding:8px;">No results found.</p>';
        return;
      }
      results.innerHTML = data.DataSource.map(r => `
        <div onclick="selectClaimRestaurant(${r.Id}, '${(r.Name||'').replace(/'/g,"\\'")}', '${(r.City||'').replace(/'/g,"\\'")}' )"
          style="padding:12px 14px;border-radius:8px;cursor:pointer;border-bottom:1px solid var(--border);transition:background 0.15s;"
          onmouseover="this.style.background='var(--hover)'" onmouseout="this.style.background=''">
          <div style="font-weight:600;font-size:14px;">${r.Name||'—'}</div>
          <div style="font-size:12px;color:var(--muted);">${r.City||''} ${r.Country||''}</div>
        </div>
      `).join('');
    } catch(e) {
      document.getElementById('claimResults').innerHTML = '<p style="color:var(--muted);font-size:13px;padding:8px;">Search unavailable. Try WhatsApp.</p>';
    }
  }, 350);
}

async function selectClaimRestaurant(placeId, name, city) {
  const status = document.getElementById('claimStatus');
  status.style.color = 'var(--muted)';
  status.textContent = 'Submitting claim request...';
  try {
    const res = await kwbPost('/Place/ClaimEstablishment', {
      IdToken: currentUser.Token,
      UserId: currentUser.Id,
      PlaceId: placeId
    });
    const data = await res.json();
    if (data && (data.Success || data.DataSource)) {
      status.style.color = 'var(--green)';
      status.textContent = `✓ Claim submitted for "${name}" — you'll get access once approved.`;
      document.getElementById('claimSearch').disabled = true;
      document.getElementById('claimResults').innerHTML = '';
    } else {
      status.style.color = '#e74c3c';
      status.textContent = 'Something went wrong. Please WhatsApp us.';
    }
  } catch(e) {
    status.style.color = '#e74c3c';
    status.textContent = 'Connection error. Please try again or WhatsApp us.';
  }
}'''

# Find and replace the old handleGoogleCredential function
pattern = r'async function handleGoogleCredential\(response\)[\s\S]*?^}'
replacement_done = False

# Try multiline replace
lines = html.split('\n')
start_idx = None
brace_count = 0
end_idx = None

for i, line in enumerate(lines):
    if 'async function handleGoogleCredential' in line and start_idx is None:
        start_idx = i
        brace_count = line.count('{') - line.count('}')
    elif start_idx is not None:
        brace_count += line.count('{') - line.count('}')
        if brace_count <= 0:
            end_idx = i
            break

if start_idx is not None and end_idx is not None:
    new_lines = lines[:start_idx] + NEW_HANDLE.split('\n') + lines[end_idx+1:]
    html = '\n'.join(new_lines)
    print(f"✓ Replaced handleGoogleCredential (lines {start_idx}–{end_idx})")
else:
    print("✗ Could not find handleGoogleCredential — check file path")
    sys.exit(1)

with open(filepath, 'w') as f:
    f.write(html)

print("✓ File patched successfully")
print(f"  Path: {filepath}")
