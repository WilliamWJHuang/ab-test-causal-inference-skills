# Contributing to Causal Data Science Skills

Thank you for your interest in improving statistical rigor in AI-assisted data science!

## How to Contribute

### Adding Reference Documents
1. Identify a gap in the `references/` directory of any skill
2. Write a focused guide following the existing style (imperative, actionable, with code examples)
3. Keep each reference document under 300 lines
4. Submit a PR with a clear description of what the guide covers

### Reporting Issues
- If you find **incorrect statistical guidance**, please open an issue with:
  - The specific claim or instruction that is wrong
  - A citation or explanation of why it's wrong
  - The corrected guidance

### Adding Code Templates
- Templates should work with standard Python data science libraries (numpy, scipy, statsmodels, pandas)
- Include docstrings with clear parameter descriptions
- Add inline comments explaining statistical choices
- Prefer functions over scripts for reusability

### Style Guide for SKILL.md Files
- Use imperative voice ("Run the test", not "You should run the test")
- Keep SKILL.md body under 400 lines
- Use numbered steps for sequential workflows
- Use decision trees (if/then) for method selection
- Include "NEVER" constraints for common errors
- Provide escape hatches for experienced users

### Testing Your Changes
1. Install the modified skill in your agent's skill directory
2. Test with at least 3 different trigger phrases
3. Verify the skill produces correct statistical guidance
4. Check that progressive disclosure works (references load on demand)

## Code of Conduct
Be rigorous, be kind, be clear. Statistical disagreements should be resolved with citations.
