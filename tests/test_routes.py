from fastapi.testclient import TestClient
from src.main import app

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
    assert pay_response.json()["detail"] == "Customer not found"

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
    assert pay_response.json()["detail"] == "Invalid amount"

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
    assert capture_res.json()["detail"] == "Payment not found"

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
    assert capture_again_res.json()["detail"] == "Payment cannot be captured"