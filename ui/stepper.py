from __future__ import annotations

import streamlit as st


def render_stepper(current_step: int, steps: list[str] | None = None):
    """Render an HTML/CSS step progress indicator."""
    if steps is None:
        steps = ["Load", "Configure", "Results"]

    n = len(steps)

    nodes_html = []
    for i, label in enumerate(steps, start=1):
        if i < current_step:
            cls = "step-node step-done"
            symbol = "✓"
        elif i == current_step:
            cls = "step-node step-active"
            symbol = str(i)
        else:
            cls = "step-node step-todo"
            symbol = str(i)

        nodes_html.append(
            f'<div class="{cls}" aria-label="Step {i}: {label}" '
            f'aria-current="{"step" if i == current_step else "false"}">'
            f'{symbol}</div>'
        )
        if i < n:
            line_cls = "step-line step-line-done" if i < current_step else "step-line step-line-todo"
            nodes_html.append(f'<div class="{line_cls}"></div>')

    labels_html = "".join(
        f'<span style="font-weight:{"700" if i+1 == current_step else "400"}">{s}</span>'
        for i, s in enumerate(steps)
    )

    html = f"""
    <div class="stepper-container" role="navigation" aria-label="Progress steps">
        {"".join(nodes_html)}
    </div>
    <div class="step-labels">{labels_html}</div>
    """
    st.markdown(html, unsafe_allow_html=True)
