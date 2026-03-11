BEIGE_THEME = {
    "config": {
        "primaryColor":             "#92400e",
        "backgroundColor":          "#fdf8f0",
        "secondaryBackgroundColor": "#f5ebe0",
        "textColor":                "#1c1410",
    },
    "css": """
<style>
:root {
    --primary:      #92400e;
    --bg:           #fdf8f0;
    --sidebar-bg:   #f5ebe0;
    --text:         #1c1410;
    --border:       #d6b896;
    --card-bg:      #f5ebe0;
    --badge-green:  #15803d;
    --badge-amber:  #92400e;
    --badge-red:    #b91c1c;
    --badge-neutral:#6b5444;
    --success-bg:   #dcfce7;
    --success-text: #14532d;
    --warning-bg:   #fef3c7;
    --warning-text: #78350f;
    --error-bg:     #fee2e2;
    --error-text:   #7f1d1d;
    --stepper-done: #92400e;
    --stepper-active: #92400e;
    --stepper-todo: #b0856b;
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

.callout-success { background: var(--success-bg); color: var(--success-text); border-left: 4px solid #16a34a; padding: 12px 16px; border-radius: 4px; margin: 8px 0; }
.callout-warning { background: var(--warning-bg); color: var(--warning-text); border-left: 4px solid #d97706; padding: 12px 16px; border-radius: 4px; margin: 8px 0; }
.callout-error   { background: var(--error-bg);   color: var(--error-text);   border-left: 4px solid #dc2626; padding: 12px 16px; border-radius: 4px; margin: 8px 0; }

.stepper-container { display: flex; align-items: center; gap: 0; margin: 12px 0; }
.step-node { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; flex-shrink: 0; }
.step-done    { background: var(--stepper-done);   color: #fff; }
.step-active  { background: var(--stepper-active); color: #fff; box-shadow: 0 0 0 3px rgba(146,64,14,0.25); }
.step-todo    { background: #e7d8c9; color: var(--stepper-todo); }
.step-line    { flex: 1; height: 3px; }
.step-line-done { background: var(--stepper-done); }
.step-line-todo { background: #e7d8c9; }
.step-labels  { display: flex; justify-content: space-between; font-size: 11px; color: var(--text); margin-top: 4px; }

*:focus-visible { outline: 3px solid var(--primary); outline-offset: 2px; }
</style>
""",
}
