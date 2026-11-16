=== stories/1-1-enrol-authenticator.md ===
# Story 1.1: Enrol an authenticator app
Status: ready-for-dev

## Story
As an account holder, I want to enrol my authenticator app by scanning a QR code, so that my sign-in is protected by a second factor.

## Acceptance Criteria
- AC-1: Given a signed-in user with no 2FA, when they open the enrolment page, then a QR code encoding a new TOTP secret is shown and the secret is not yet active.
- AC-2: Given a displayed QR code, when the user submits a code their app generated, then enrolment completes and 2FA becomes active.
- AC-3: Given a displayed QR code, when the user submits a wrong code, then enrolment does not complete and the secret stays inactive.

## Tasks / Subtasks
- [ ] Generate a TOTP secret and render it as a QR code (AC: 1)
- [ ] Verify the confirmation code and activate 2FA only on success (AC: 2, 3)

## Dev Notes
- FR-1 is the requirement behind this story.
- `totp_secret` is a new column on the users table; verification uses pyotp.

### References
- [Source: docs/prd.md#FR-1]
- [Source: docs/architecture.md#data-model]

=== stories/1-2-totp-at-login.md ===
# Story 1.2: Require a TOTP code at sign-in
Status: ready-for-dev

## Story
As an account holder with 2FA enabled, I want to be asked for a TOTP code after my password, so that a stolen password alone cannot sign in as me.

## Acceptance Criteria
- AC-1: Given a user with 2FA enabled, when they submit a correct password, then they are asked for a TOTP code and no session is created yet.
- AC-2: Given the TOTP prompt, when a valid code is submitted, then the session is created.
- AC-3: Given the TOTP prompt, when an invalid code is submitted, then no session is created and the user stays on the prompt.

## Tasks / Subtasks
- [ ] Split login into password and TOTP steps (AC: 1)
- [ ] Verify the code and create the session only on success (AC: 2, 3)

## Dev Notes
- FR-2 is the requirement behind this story.
- Verification uses pyotp against the stored `totp_secret`.

### References
- [Source: docs/prd.md#FR-2]
- [Source: docs/architecture.md#verification]

=== stories/1-3-recovery-codes.md ===
# Story 1.3: Recovery code support
Status: ready-for-dev

## Story
As an account holder, I want recovery code support, so that the feature is complete.

## Acceptance Criteria
- AC-1: Given the recovery code feature, when it is implemented, then the behaviour is covered by a test.
- AC-2: Given the implementation, when the test suite runs, then it passes.

## Tasks / Subtasks
- [ ] Implement recovery codes (AC: 1)
- [ ] Add tests (AC: 2)

## Dev Notes
- FR-3 is the requirement behind this story.
- `recovery_codes` is a new column on the users table.

### References
- [Source: docs/prd.md#FR-3]
- [Source: docs/architecture.md#data-model]
