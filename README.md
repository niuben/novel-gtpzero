# TextCheck

AI 味逐行改写 MVP。输入整篇文章，后端按换行拆成行，用 `jieba` 自定义词典识别规则，生成低风险修改建议；前端展示每行修改前后，支持单行确认和全局确认。

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

接口：

```text
GET  /health
POST /api/process
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

访问：

```text
http://localhost:5173
```

## MVP Scope

- 解析层：按回车和空行拆分文章。
- 规则层：维护删除、替换、提示三类规则。
- 执行层：只自动执行低风险删除和替换。
- 校验层：保护否定词、数字和过大改动。
- 展示层：展示逐行修改前后，支持人工确认。

当前不会自动补数字、案例、主语、场景或因果关系。
