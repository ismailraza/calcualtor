# AI Social Media Automation Starter

This project is a minimal starter for automating social media content creation with AI.

## What it does
- Generates a caption and hashtags from a topic.
- Generates an image using the OpenAI Images API.
- Saves the output in a local `output/` folder.
- Optionally simulates posting to social media platforms through a local JSON log.

## Why this starter
A fully automatic posting system should still include a human review checkpoint to avoid policy violations, spam, or accidental bad posts. This starter defaults to `dry-run` mode and writes the final payload to disk.

## Quick start

1. Create a virtual environment and install dependencies.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Set your API key.

```bash
export OPENAI_API_KEY="your_key_here"
```

3. Generate content for a topic.

```bash
python social_automation.py generate \
  --topic "AI productivity hacks" \
  --brand "YourBrand" \
  --platform instagram
```

4. Review and optionally "post".

```bash
python social_automation.py post --input output/latest_post.json --dry-run
```

## Example workflow
1. `generate` step creates a JSON payload with:
   - caption
   - hashtags
   - image prompt
   - local image path
2. Edit the JSON manually if needed.
3. Run `post` to dry run or real post integration.

## Extending to real platforms
Replace the `publish_to_platform` function in `social_automation.py` with real API integrations:
- Instagram Graph API
- X API
- LinkedIn API
- TikTok API

## Safety checklist
- Keep a manual review step.
- Add profanity / policy filters.
- Avoid posting copyrighted logos in generated images.
- Respect each platform's API terms and rate limits.
