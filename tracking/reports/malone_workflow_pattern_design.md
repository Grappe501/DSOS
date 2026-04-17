# Workflow pattern design

## When selected

Process-oriented phrasing (“walk me through”, “next steps”, “procedure”, …) and/or workflow-typed normalized units / escalation cues.

## Answer shape

1. Disclaimer + pattern label  
2. **Situation / question** (user message truncated)  
3. **Ordered steps** from `decision_workflow.action_steps` when decision layer emits structured sections; otherwise an explicit partial notice  
4. **Escalation / stop** lines from decision workflow when available  
5. **Sources**: full citation/segment blocks  

Decision/workflow appendix is still appended uniformly by integration after pattern body.
