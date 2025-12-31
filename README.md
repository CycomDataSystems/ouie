# AI Eval: OUIE
Overconfidence Under Insufficient Evidence (OUIE)

## Failure Hypothesis
When information is insufficient, the model produces confident-sounding answers instead of expressing uncertainty or asking for clarification.

## Scope
(What this eval does and does not test.)
### It does test
- Epistemic honesty
- Calibration under uncertainty
- Pressure from authoritative framing

### It does NOT test
- Factual knowledge
- Policy compliance
- Malicious intent
- Adversarial jailbreaks

## How to run
1. Set up venv
2. Copy `examples.env` to `.env` and fill in your OpenAI API key.
3. `python run_eval.py`
4. `python scripts/export_csv.py results/<model>.jsonl`