# Custom Labels, IAM, and human review

Source: docs.aws.amazon.com (rekognition/latest/customlabels-dg, rekognition/latest/dg/security-iam.html). Fetched 2026-09.

## Rekognition Custom Labels

For object/scene detection needs the built-in `DetectLabels` catalog doesn't cover — train a model on your own images instead of the general-purpose one.

- Needs meaningfully **less data** than training a model from scratch: typically a few hundred images per class or fewer, versus the thousands/tens-of-thousands a general model needs.
- Workflow: create a **project** → create **training and test datasets** (images + labels) → **train** → evaluate performance metrics → use the resulting model through the Custom Labels API.
- Dataset sourcing options: import from a local machine (unlabeled — you label afterward in-console), from an S3 bucket (can auto-label by folder name), from a SageMaker Ground Truth manifest (pre-labeled), or by copying an existing Custom Labels dataset.
- If you start a project with a **single** dataset rather than separate training/test sets, the console **splits it roughly 80/20** (training/test) automatically. Use a single dataset when you're fine letting the split happen for you; provide separate training and test datasets when you need full control over what's used for evaluation versus training.
- **You're billed for training time** — training isn't free compute, and re-training (e.g. iterating on dataset quality) accumulates cost accordingly.
- Optional: encrypt training data with a customer-managed KMS key instead of the default, and tag models like any other resource.
- Trade-offs versus building a fully custom pipeline: automated and low-effort, supports multi-label classification — but you don't control the objective function, network architecture, or initial weights, and the automated tune/train cycle can be slower and pricier than a fully custom pipeline for frequent retraining.
- Once trained, a Custom Labels model can be referenced from `DetectLabels` via `ProjectVersionArn` to blend custom predictions alongside the built-in label catalog (see `image-analysis.md`).

## IAM least privilege

Standard IAM hygiene applies, with a couple of Rekognition-specific notes:

- Start from an AWS managed policy for common use cases, then narrow to a customer-managed policy scoped to your actual actions/resources — don't leave broad managed policies attached long-term.
- Video job notification needs a **service role** trusted by Rekognition that can `sns:Publish` to your specific topic — scope this role tightly to that one topic, not broad SNS access.
- Tagging a stream processor or Custom Labels model requires `rekognition:TagResource` in addition to the resource-creation permission — a common "why did tagging fail but creation succeed" gap.
- Use IAM Access Analyzer to validate policies before attaching them, and add SSL/MFA conditions where appropriate — the same general IAM discipline covered in depth elsewhere (see the IAM-focused guidance this toolkit or your organization already applies).

## Human review via Amazon A2I

`DetectModerationLabels` integrates directly with **Amazon Augmented AI (A2I)** to route low-confidence or randomly sampled predictions to human reviewers, with a built-in workflow (worker UI, activation conditions by confidence threshold or sampling percentage, results saved to S3).

> **A2I is no longer open to new customers.** Existing customers can continue using it; AWS continues security/availability maintenance but isn't adding new features. **Don't design a new moderation pipeline assuming A2I is available** — build your own human-review queue (e.g. route low-confidence `DetectModerationLabels` results to a queue via SQS/EventBridge for manual review) instead, unless you already have A2I access on the account.

## Pitfalls

- Starting Custom Labels training with too few or unrepresentative images per class and being surprised by poor model performance — the "few hundred per class" guidance is a floor, not a guarantee.
- Forgetting `rekognition:TagResource` when a tagged creation call otherwise succeeds.
- Assuming A2I is available for a new moderation pipeline without checking current account eligibility — build a custom human-review queue instead if it isn't.
- Granting broad SNS or S3 access to a Rekognition service role instead of scoping it to the specific topic/bucket the job actually needs.
