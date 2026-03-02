# Combining Verification Patterns


## Contents

- [Table of Contents](#table-of-contents)
- [5.1 Pattern Combinations](#51-pattern-combinations)
- [5.2 Verification Pyramid](#52-verification-pyramid)
- [5.3 Complete Verification Strategy Example](#53-complete-verification-strategy-example)

---

## Table of Contents

- [5.1 Pattern Combinations](#51-pattern-combinations)
  - 5.1.1 Evidence-based verification + Unit tests
  - 5.1.2 Exit code proof + Scripts
  - 5.1.3 Integration verification + Component tests
  - 5.1.4 E2E testing for complete systems
- [5.2 Verification Pyramid](#52-verification-pyramid)
  - 5.2.1 Layer structure from bottom to top
  - 5.2.2 Layer dependencies
- [5.3 Complete Verification Strategy Example](#53-complete-verification-strategy-example)
  - 5.3.1 All four layers in one workflow

---

## 5.1 Pattern Combinations

The four verification patterns work together. Use them in combination:

| Combination | Purpose |
|-------------|---------|
| Evidence-based verification + Unit tests | Prove individual functions work |
| Exit code proof + Scripts | Build reliable automation |
| Integration verification + Component tests | Prove components work together |
| E2E testing | Prove the complete system works |

---

## 5.2 Verification Pyramid

From bottom to top:

```
         E2E Tests (few, slow, high value)
      Integration Tests (moderate, medium speed)
      Unit Tests (many, fast, evidence-based)
   Exit Code Proof (everywhere)
```

Each layer depends on the layers below it.

| Layer | Count | Speed | Value |
|-------|-------|-------|-------|
| Exit Code Proof | Everywhere | Instant | Foundation |
| Unit Tests | Many | Fast | Confidence in functions |
| Integration Tests | Moderate | Medium | Confidence in components |
| E2E Tests | Few | Slow | Confidence in system |

---

## 5.3 Complete Verification Strategy Example

```python
# Layer 1: Unit test with evidence-based verification
def test_add_function():
    # Evidence: return value
    result = add(2, 3)
    assert result == 5, f"Expected 5, got {result}"

# Layer 2: Exit code proof in automation script
#!/bin/bash
python3 -m pytest
if [ $? -ne 0 ]; then
    echo "Tests failed"
    exit 1
fi

# Layer 3: Integration test
def test_api_and_database():
    response = requests.post('/users', json={'name': 'Alice'})
    assert response.status_code == 201
    # Also verify database
    db_user = database.find_user('Alice')
    assert db_user is not None

# Layer 4: E2E test
def test_complete_workflow():
    driver.get('http://localhost:3000')
    driver.find_element(By.ID, 'register-btn').click()
    # ... complete workflow ...
    assert driver.find_element(By.ID, 'success-message').is_displayed()
```
