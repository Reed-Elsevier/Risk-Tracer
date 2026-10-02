# ECS (API only)

Image built by GitHub Actions (no Docker on the laptop):

`ghcr.io/reed-elsevier/risk-tracer/api:main`

Next.js stays on Amplify. This task is the FastAPI process on port **8000**.

The running API calls **OpenAI**, not Bedrock. `/investigate` works without a key. `/investigate/explain` needs `OPENAI_API_KEY`.

## 1. Make the package pullable

GitHub → Packages → `api` → Package settings → **Public**.

If it must stay private, add `repositoryCredentials` on the container pointing at a Secrets Manager secret `{"username":"<github-user>","password":"<read:packages PAT>"}`.

## 2. Replace placeholders

In `task-definition.json` replace:

- `ACCOUNT_ID`
- `AWS_REGION` (example `ap-southeast-1`)
- `https://AMPLIFY_APP_ID.amplifyapp.com` with the real Amplify origin

Create the log group and the OpenAI secret (do not commit the key):

```bash
aws logs create-log-group --log-group-name /ecs/risktracer-api --region AWS_REGION

aws secretsmanager create-secret \
  --name risktracer/openai-api-key \
  --secret-string "sk-..." \
  --region AWS_REGION
```

The execution role needs `AmazonECSTaskExecutionRolePolicy` and `secretsmanager:GetSecretValue` on that secret. If you skip explain for the demo, delete the `secrets` block instead of creating the secret.

## 3. Register the task

```bash
aws ecs create-cluster --cluster-name risktracer --region AWS_REGION

aws ecs register-task-definition \
  --cli-input-json file://deploy/ecs/task-definition.json \
  --region AWS_REGION
```

## 4. Network

- ALB security group: inbound **80** from `0.0.0.0/0`
- API security group: inbound **8000** from the ALB security group only
- Target group: IP, HTTP, port **8000**, health path `/health`, interval 30s
- Service: Fargate, public subnets, **assign public IP**, desired count 1

First boot loads the CSVs. Wait until the target is **healthy** (can take a few minutes) before calling it.

## 5. Prove it

```powershell
$base = "http://YOUR-ALB-DNS-NAME"
Invoke-RestMethod "$base/health"
Invoke-RestMethod -Method POST "$base/investigate" -ContentType "application/json" -Body '{"invoice_id":"INV0021439"}'
```

## 6. Amplify

Set `NEXT_PUBLIC_API_URL` to `http://YOUR-ALB-DNS-NAME` (no trailing slash) and redeploy the frontend. Use HTTPS on the ALB if the Amplify site is HTTPS, or the browser will block the API call.
