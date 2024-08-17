# How to run

```shell
pip install poetry

poetry lock
poetry install

OPENAI_BASE_URL=https://api.siliconflow.cn/v1 OPENAI_API_KEY=your_siliconflow_key OPENAI_LOG=debug poetry run python jike_roast/app.py
```
