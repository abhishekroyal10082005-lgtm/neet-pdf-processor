* {
  box-sizing: border-box;
}

:root {
  --bg: #f5f3ff;
  --panel: rgba(255, 255, 255, 0.72);
  --card: #ffffff;
  --card-border: rgba(94, 82, 155, 0.08);
  --text: #1a1b2e;
  --muted: #5e647d;
  --primary: #4f46e5;
  --primary-soft: #ece9ff;
  --success: #1d7f5a;
  --warning: #d97706;
  --danger: #b42318;
  --shadow: 0 16px 36px rgba(79, 70, 229, 0.08);
}

html, body, #root {
  margin: 0;
  height: 100%;
  font-family: Inter, 'Segoe UI', sans-serif;
  background: linear-gradient(135deg, #f8f6ff 0%, #eef2ff 100%);
  color: var(--text);
}

button, input, select {
  font: inherit;
}

button {
  border: none;
  cursor: pointer;
}

.app-shell {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 260px;
  padding: 32px 20px;
  border-right: 1px solid rgba(79, 70, 229, 0.08);
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: white;
  font-weight: 800;
}

.brand-name {
  font-weight: 700;
}

.brand-block small {
  color: var(--muted);
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.nav-item {
  background: transparent;
  text-align: left;
  padding: 12px 14px;
  border-radius: 12px;
  color: var(--text);
  font-weight: 600;
}

.nav-item.active {
  background: var(--primary-soft);
  color: var(--primary);
}

.main-panel {
  flex: 1;
  padding: 24px 28px 36px;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.eyebrow {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  font-size: 11px;
}

.topbar h1 {
  margin: 6px 0 0;
  font-size: 2.2rem;
}

.top-actions {
  display: flex;
  gap: 12px;
}

.primary-btn, .secondary-btn {
  border-radius: 12px;
  padding: 11px 16px;
  font-weight: 600;
}

.primary-btn {
  background: linear-gradient(135deg, var(--primary), #7c3aed);
  color: white;
}

.secondary-btn {
  background: #f4f2ff;
  color: var(--primary);
}

.card {
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: 20px;
  box-shadow: var(--shadow);
  padding: 22px;
}

.hero-grid,
.content-grid,
.bottom-grid {
  display: grid;
  gap: 20px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
  font-weight: 600;
}

.metric-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 18px;
}

.label {
  color: var(--muted);
  font-size: 12px;
  margin-bottom: 8px;
}

.value {
  font-size: 32px;
  font-weight: 800;
}

.progress-block {
  display: grid;
  gap: 8px;
}

.progress-bar {
  height: 10px;
  background: #f2f1ff;
  border-radius: 999px;
  overflow: hidden;
}

.progress-bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #4f46e5, #8b5cf6);
}

.progress-meta {
  display: flex;
  justify-content: space-between;
  color: var(--muted);
  font-size: 12px;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  text-transform: capitalize;
  background: rgba(29, 127, 90, 0.12);
  color: var(--success);
}

.status-pill.processing {
  background: rgba(217, 119, 6, 0.12);
  color: var(--warning);
}

.status-pill.cancelled,
.status-pill.failed {
  background: rgba(180, 35, 24, 0.12);
  color: var(--danger);
}

.status-pill.neutral {
  background: #eef2ff;
  color: #4b5563;
}

.muted {
  color: var(--muted);
}

.small {
  font-size: 12px;
}

.feature-list {
  list-style: none;
  display: grid;
  gap: 8px;
  padding: 0;
  margin: 14px 0 0;
  color: var(--muted);
}

.field-label {
  display: block;
  margin: 14px 0 8px;
  font-weight: 600;
}

input[type='text'], input[type='file'], input[type='range'], select {
  width: 100%;
}

input[type='text'], select {
  border: 1px solid rgba(79, 70, 229, 0.12);
  background: #fbfaff;
  border-radius: 12px;
  padding: 11px 12px;
  color: var(--text);
}

input[type='file'] {
  border: 1px dashed rgba(79, 70, 229, 0.18);
  border-radius: 12px;
  background: #faf8ff;
  padding: 12px;
}

.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 16px;
}

.check-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--muted);
  text-transform: capitalize;
}

.button-row {
  margin-top: 20px;
}

.job-list,
.file-list {
  display: grid;
  gap: 12px;
}

.job-item,
.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid rgba(94, 82, 155, 0.08);
  border-radius: 14px;
  background: #faf9ff;
}

.job-meta {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.small-value {
  font-size: 12px;
  color: var(--muted);
}

.job-actions {
  display: flex;
  gap: 8px;
}

.error-banner {
  background: rgba(180, 35, 24, 0.08);
  color: var(--danger);
  border: 1px solid rgba(180, 35, 24, 0.12);
  border-radius: 12px;
  padding: 12px 14px;
  margin-bottom: 22px;
}

.settings-grid {
  display: grid;
  gap: 20px;
}

.settings-grid label {
  display: block;
  margin-bottom: 8px;
  color: var(--muted);
}

input[type='range'] {
  accent-color: var(--primary);
}

@media (max-width: 940px) {
  .app-shell {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid rgba(79, 70, 229, 0.08);
  }

  .hero-grid,
  .content-grid,
  .bottom-grid {
    grid-template-columns: 1fr;
  }

  .topbar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
