# reCAPTCHA v2 Auto Challenge

Based on image recognition. A lightweight toolkit for automating reCAPTCHA v2 challenges. This repository provides Python scripts to run an API server and an automated challenge workflow, with pretrained model artifacts and labeled datasets available upon donation.

## Features
- Automates reCAPTCHA v2 challenge workflow
- Simple Python entry points for API and automation
- Pluggable model files under `models/`
- Ready for local usage and integration into pipelines

## Repository Structure
- `api_server.py` — API server entry for challenge services
- `auto_challenge.py` — Automated reCAPTCHA v2 challenge runner
- `models/` — Pretrained model artifacts (e.g. `best 9.20.pt`)
- `utils/translations.py` — Helper utilities (e.g., translations)
- `test.py` — Basic test entry

## Quick Start
Start the API server:

```bash
python api_server.py
```

Run the automation test script:
```bash
python test.py
```

## Models and Labeled Data
- Model artifacts are located in `models/` and are distributed upon donation.
- Labeled datasets are available as part of the donation package.

## Donation
- Wallet Address: `0xa6713dc33583741a65e9ae3954b0578f52d74d42`
- Network: BNB Chain
- Amount: 10 USDT

### How to Receive Files
After donating 10 USDT on BNB Chain:
- Send the email to admin@easamail.com and include the transaction hash.
- You will receive access to the model files (`models/`) and labeled data.

## Notes
- Ensure you are sending USDT on BNB Chain (BEP-20) to the wallet address above.

## Disclaimer
- This project is provided for research and educational purposes.
- Respect terms of service and legal restrictions of the platforms you interact with.
- The authors and contributors are not responsible for misuse or any violation of third-party policies.

## License
- Unless otherwise specified, all rights reserved.
- For commercial use or redistribution, please contact the repository owner.
