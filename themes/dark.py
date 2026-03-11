DARK_THEME = {
    "config": {
        "primaryColor":             "#38bdf8",
        "backgroundColor":          "#0f172a",
        "secondaryBackgroundColor": "#1e293b",
        "textColor":                "#f1f5f9",
    },
    "css": """
<style>
:root {
    --primary:      #38bdf8;
    --bg:           #0f172a;
    --sidebar-bg:   #1e293b;
    --text:         #f1f5f9;
    --border:       #334155;
    --card-bg:      #1e293b;
    --badge-green:  #15803d;
    --badge-amber:  #92400e;
    --badge-red:    #b91c1c;
    --badge-neutral:#64748b;
    --success-bg:   #14532d;
    --success-text: #bbf7d0;
    --warning-bg:   #78350f;
    --warning-text: #fde68a;
    --error-bg:     #7f1d1d;
    --error-text:   #fecaca;
    --stepper-done: #38bdf8;
    --stepper-active: #38bdf8;
    --stepper-todo: #475569;
}

.stApp {
    background-color: var(--bg);
    color: var(--text);
}

section[data-testid="stSidebar"] {
    background-color: var(--sidebar-bg);
}

.metric-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    text-align: center;
    color: var(--text);
}

.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    color: #ffffff;
}

.badge-green  { background: var(--badge-green);  }
.badge-amber  { background: var(--badge-amber);  }
.badge-red    { background: var(--badge-red);    }
.badge-neutral{ background: var(--badge-neutral); font-style: italic; }

.callout-success { background: var(--success-bg); color: var(--success-text); border-left: 4px solid #22c55e; padding: 12px 16px; border-radius: 4px; margin: 8px 0; }
.callout-warning { background: var(--warning-bg); color: var(--warning-text); border-left: 4px solid #f59e0b; padding: 12px 16px; border-radius: 4px; margin: 8px 0; }
.callout-error   { background: var(--error-bg);   color: var(--error-text);   border-left: 4px solid #ef4444; padding: 12px 16px; border-radius: 4px; margin: 8px 0; }

.stepper-container { display: flex; align-items: center; gap: 0; margin: 12px 0; }
.step-node { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; flex-shrink: 0; }
.step-done    { background: var(--stepper-done);   color: #0f172a; }
.step-active  { background: var(--stepper-active); color: #0f172a; box-shadow: 0 0 0 3px rgba(56,189,248,0.25); }
.step-todo    { background: #334155; color: var(--stepper-todo); }
.step-line    { flex: 1; height: 3px; }
.step-line-done { background: var(--stepper-done); }
.step-line-todo { background: #334155; }
.step-labels  { display: flex; justify-content: space-between; font-size: 11px; color: var(--text); margin-top: 4px; }

*:focus-visible { outline: 3px solid var(--primary); outline-offset: 2px; }
</style>
""",
}
