from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import patch

# Create a test client to simulate API requests
client = TestClient(app)

def test_create_payment_success():
    # 1. First, we need a valid customer to attach the payment to
    cust_response = client.post("/customers", json={"name": "Charlie", "email": "charlie@example.com"})
    assert cust_response.status_code == 201
    customer_id = cust_response.json()["id"]

    # 2. Now, create the payment for that customer
    pay_response = client.post("/payments", json={
        "customer_id": customer_id,
        "amount": 1500,  # 1500 pence/cents
        "currency": "usd"
    })
    
    assert pay_response.status_code == 201
    assert pay_response.json()["status"] == "pending"
    assert "id" in pay_response.json()

def test_create_payment_fails_for_invalid_customer():
    pay_response = client.post("/payments", json={
        "customer_id": "cus_invalid999",
        "amount": 1000,
        "currency": "usd"
    })
    
    # Assuming your spec requires a 404 for a missing customer
    assert pay_response.status_code == 404 
    assert pay_response.json()["error"] == "Customer not found"

def test_create_payment_fails_for_invalid_amount():
    # Re-create a user for this specific test
    cust_response = client.post("/customers", json={"name": "Dave", "email": "dave@example.com"})
    customer_id = cust_response.json()["id"]

    pay_response = client.post("/payments", json={
        "customer_id": customer_id,
        "amount": -50,  # Invalid amount (must be >= 1)
        "currency": "usd"
    })
    
    assert pay_response.status_code == 400
    assert pay_response.json()["error"] == "Invalid amount"

    # ... (previous tests remain above this) ...

def test_capture_payment_returns_200_and_updated_payment():
    # 1. Setup: Create customer and payment
    cust_res = client.post("/customers", json={"name": "Eve", "email": "eve@example.com"})
    customer_id = cust_res.json()["id"]
    
    pay_res = client.post("/payments", json={"customer_id": customer_id, "amount": 5000, "currency": "usd"})
    payment_id = pay_res.json()["id"]
    assert pay_res.json()["status"] == "pending"

    # 2. Action: Capture the payment
    capture_res = client.post(f"/payments/{payment_id}/capture")
    
    # 3. Assert: 200 OK and status is succeeded
    assert capture_res.status_code == 200
    assert capture_res.json()["status"] == "succeeded"
    assert capture_res.json()["id"] == payment_id

def test_capture_payment_returns_404_when_id_is_unknown():
    capture_res = client.post("/payments/pay_unknown999/capture")
    
    assert capture_res.status_code == 404
    assert capture_res.json()["error"] == "Payment not found"

def test_capture_payment_returns_409_when_cannot_be_captured():
    # 1. Setup: Create customer and payment
    cust_res = client.post("/customers", json={"name": "Frank", "email": "frank@example.com"})
    customer_id = cust_res.json()["id"]
    
    pay_res = client.post("/payments", json={"customer_id": customer_id, "amount": 2000, "currency": "usd"})
    payment_id = pay_res.json()["id"]

    # 2. Capture it the first time (this will succeed)
    client.post(f"/payments/{payment_id}/capture")

    # 3. Action: Try to capture it again
    capture_again_res = client.post(f"/payments/{payment_id}/capture")
    
    # 4. Assert: 409 Conflict because it's no longer 'pending'
    assert capture_again_res.status_code == 409
    assert capture_again_res.json()["error"] == "Payment cannot be captured"

    # ... (previous tests remain above this) ...

def test_create_refund_success():
    # 1. Setup: Create customer and payment
    cust_res = client.post("/customers", json={"name": "Grace", "email": "grace@example.com"})
    customer_id = cust_res.json()["id"]
    
    pay_res = client.post("/payments", json={"customer_id": customer_id, "amount": 3000, "currency": "usd"})
    payment_id = pay_res.json()["id"]

    # 2. Action: Create a refund
    refund_res = client.post("/refunds", json={"paymentId": payment_id, "amount": 1000})
    
    # 3. Assert: 201 Created and refund object is returned
    assert refund_res.status_code == 201
    assert "id" in refund_res.json()
    assert refund_res.json()["paymentId"] == payment_id
    assert refund_res.json()["amount"] == 1000

def test_create_refund_returns_400_when_payment_id_is_missing():
    refund_res = client.post("/refunds", json={"amount": 1000})
    
    assert refund_res.status_code == 400
    assert refund_res.json()["error"] == "paymentId is missing"

def test_create_refund_returns_400_when_amount_is_missing():
    refund_res = client.post("/refunds", json={"paymentId": "pay_some123"})
    
    assert refund_res.status_code == 400
    assert refund_res.json()["error"] == "amount is missing"

def test_create_refund_returns_422_when_amount_exceeds_payment():
    # 1. Setup: Create customer and payment of 1500
    cust_res = client.post("/customers", json={"name": "Heidi", "email": "heidi@example.com"})
    customer_id = cust_res.json()["id"]
    pay_res = client.post("/payments", json={"customer_id": customer_id, "amount": 1500, "currency": "usd"})
    payment_id = pay_res.json()["id"]

    # 2. Action: Try to refund 2000
    refund_res = client.post("/refunds", json={"paymentId": payment_id, "amount": 2000})
    
    # 3. Assert: 422 Unprocessable Entity
    assert refund_res.status_code == 422
    assert refund_res.json()["error"] == "Refund amount exceeds payment amount"

def test_get_all_payments_returns_200_and_list():
    # 1. Setup: Create a customer and payment so the list isn't empty
    cust_res = client.post("/customers", json={"name": "Ivan", "email": "ivan@example.com"})
    customer_id = cust_res.json()["id"]
    client.post("/payments", json={"customer_id": customer_id, "amount": 1000, "currency": "usd"})
    
    # 2. Action: Fetch all payments
    get_res = client.get("/payments")
    
    # 3. Assert: 200 OK, it's a list, and it contains at least our new payment
    assert get_res.status_code == 200
    assert isinstance(get_res.json(), list)
    assert len(get_res.json()) >= 1

# We use @patch to temporarily replace our service's method with a broken fake one
@patch("src.main.service.get_all_payments")
def test_get_all_payments_returns_500_on_unexpected_error(mock_get_all):
    # 1. Setup: Force the mock to raise a generic Exception
    mock_get_all.side_effect = Exception("Simulated database crash or memory error")
    
    # 2. Action: Fetch all payments
    get_res = client.get("/payments")
    
    # 3. Assert: 500 Internal Server Error
    assert get_res.status_code == 500
    assert get_res.json()["error"] == "Internal server error"    

# --- CUSTOMER BOUNDARY TESTS ---
def test_customer_name_1_character():
    res = client.post("/customers", json={"name": "A", "email": "a@example.com"})
    assert res.status_code == 201

def test_customer_name_100_characters():
    long_name = "A" * 100
    res = client.post("/customers", json={"name": long_name, "email": "a100@example.com"})
    assert res.status_code == 201

def test_customer_name_101_characters():
    too_long_name = "A" * 101
    res = client.post("/customers", json={"name": too_long_name, "email": "a101@example.com"})
    assert res.status_code == 400

# --- PAYMENT BOUNDARY TESTS ---
def test_payment_amount_minimum_1():
    cust_res = client.post("/customers", json={"name": "Bob", "email": "bob@example.com"})
    res = client.post("/payments", json={"customer_id": cust_res.json()["id"], "amount": 1, "currency": "usd"})
    assert res.status_code == 201

def test_payment_amount_0():
    res = client.post("/payments", json={"customer_id": "cus_123", "amount": 0, "currency": "usd"})
    assert res.status_code == 400

def test_payment_amount_negative_1():
    res = client.post("/payments", json={"customer_id": "cus_123", "amount": -1, "currency": "usd"})
    assert res.status_code == 400

def test_payment_amount_decimal():
    res = client.post("/payments", json={"customer_id": "cus_123", "amount": 9.99, "currency": "usd"})
    assert res.status_code == 400 # Will trigger our new RequestValidationError handler

# --- REFUND BOUNDARY TESTS ---
def test_refund_exact_amount():
    cust_res = client.post("/customers", json={"name": "Cam", "email": "cam@example.com"})
    pay_res = client.post("/payments", json={"customer_id": cust_res.json()["id"], "amount": 500, "currency": "usd"})
    
    res = client.post("/refunds", json={"paymentId": pay_res.json()["id"], "amount": 500})
    assert res.status_code == 201

def test_refund_one_penny_over():
    cust_res = client.post("/customers", json={"name": "Dan", "email": "dan@example.com"})
    pay_res = client.post("/payments", json={"customer_id": cust_res.json()["id"], "amount": 500, "currency": "usd"})
    
    res = client.post("/refunds", json={"paymentId": pay_res.json()["id"], "amount": 501})
    assert res.status_code == 422

# --- 404 NOT FOUND TESTS ---

def test_get_customer_not_found():
    res = client.get("/customers/cus_unknown999")
    assert res.status_code == 404
    assert res.json() == {"error": "Customer not found"}

def test_get_customer_payments_not_found():
    res = client.get("/customers/cus_unknown999/payments")
    assert res.status_code == 404
    assert res.json() == {"error": "Customer not found"}

def test_get_payment_not_found():
    res = client.get("/payments/pay_unknown999")
    assert res.status_code == 404
    assert res.json() == {"error": "Payment not found"}

def test_fail_payment_not_found():
    res = client.post("/payments/pay_unknown999/fail")
    assert res.status_code == 404
    assert res.json() == {"error": "Payment not found"}

def test_get_refund_not_found():
    res = client.get("/refunds/ref_unknown999")
    assert res.status_code == 404
    assert res.json() == {"error": "Refund not found"}