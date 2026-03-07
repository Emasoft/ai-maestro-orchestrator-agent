## Table of Contents
- [Example 1: Evidence-Based Verification](#example-1-evidence-based-verification)
- [Example 2: Exit Code Proof](#example-2-exit-code-proof)

---

## Example 1: Evidence-Based Verification

```python
def test_user_creation():
    # Step 1: Define expected outcome
    expected_email = "test@example.com"

    # Step 2: Run the code
    user = create_user(email=expected_email)

    # Step 3: Collect evidence
    actual_email = user.email
    db_record = db.query(User).filter_by(id=user.id).first()

    # Step 4: Compare evidence to expectation
    assert actual_email == expected_email
    assert db_record is not None
    assert db_record.email == expected_email

    # Step 5: Document results (test framework handles this)
```

## Example 2: Exit Code Proof

```bash
# Run tests and capture exit code
pytest tests/ --cov=src
exit_code=$?

# Interpret result
if [ $exit_code -eq 0 ]; then
    echo "SUCCESS: All tests passed"
else
    echo "FAILURE: Tests failed with exit code $exit_code"
    exit 1
fi
```
