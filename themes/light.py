LIGHT_THEME = {
    "config": {
        "primaryColor":             "#0369a1",
        "backgroundColor":          "#ffffff",
        "secondaryBackgroundColor": "#f0f9ff",
        "textColor":                "#0f172a",
    },
    "css": """
<style>
:root {
    --primary:      #0369a1;
    --bg:           #ffffff;
    --sidebar-bg:   #f0f9ff;
    --text:         #0f172a;
    --border:       #bae6fd;
    --card-bg:      #f0f9ff;
    --badge-green:  #15803d;
    --badge-amber:  #92400e;
    --badge-red:    #b91c1c;
    --badge-neutral:#475569;
    --success-bg:   #dcfce7;
    --success-text: #14532d;
    --warning-bg:   #fef9c3;
    --warning-text: #713f12;
    --error-bg:     #fee2e2;
    --error-text:   #7f1d1d;
    --stepper-done: #0369a1;
    --stepper-active: #0369a1;
    --stepper-todo: #94a3b8;
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
.callout-warning { background: var(--warning-bg); color: var(--warning-text); border-left: 4px solid #ca8a04; padding: 12px 16px; border-radius: 4px; margin: 8px 0; }
.callout-error   { background: var(--error-bg);   color: var(--error-text);   border-left: 4px solid #dc2626; padding: 12px 16px; border-radius: 4px; margin: 8px 0; }

.stepper-container { display: flex; align-items: center; gap: 0; margin: 12px 0; }
.step-node { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; flex-shrink: 0; }
.step-done    { background: var(--stepper-done);   color: #fff; }
.step-active  { background: var(--stepper-active); color: #fff; box-shadow: 0 0 0 3px rgba(3,105,161,0.25); }
.step-todo    { background: #e2e8f0; color: var(--stepper-todo); }
.step-line    { flex: 1; height: 3px; }
.step-line-done { background: var(--stepper-done); }
.step-line-todo { background: #e2e8f0; }
.step-labels  { display: flex; justify-content: space-between; font-size: 11px; color: var(--text); margin-top: 4px; }

*:focus-visible { outline: 3px solid var(--primary); outline-offset: 2px; }
</style>
""",
}
