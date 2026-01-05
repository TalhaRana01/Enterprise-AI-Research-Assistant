# Test API endpoints script

Write-Host "Testing AI Research Assistant API..." -ForegroundColor Green

$baseUrl = "http://localhost:8000"

# Test 1: Health Check
Write-Host "`n1. Testing Health Endpoint..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
    Write-Host "✅ Health Check: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health Check Failed: $_" -ForegroundColor Red
}

# Test 2: Root Endpoint
Write-Host "`n2. Testing Root Endpoint..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
    Write-Host "✅ Root Endpoint: $($response.message)" -ForegroundColor Green
} catch {
    Write-Host "❌ Root Endpoint Failed: $_" -ForegroundColor Red
}

# Test 3: Search Endpoint (GET)
Write-Host "`n3. Testing Search Endpoint (GET)..." -ForegroundColor Cyan
try {
    $query = "transformer models"
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/search?query=$query&max_results=3" -Method Get
    Write-Host "✅ Search: Found $($response.total) papers" -ForegroundColor Green
} catch {
    Write-Host "❌ Search Failed: $_" -ForegroundColor Red
}

# Test 4: Search Endpoint (POST)
Write-Host "`n4. Testing Search Endpoint (POST)..." -ForegroundColor Cyan
try {
    $body = @{
        query = "machine learning"
        max_results = 3
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/search" -Method Post -Body $body -ContentType "application/json"
    Write-Host "✅ Search POST: Found $($response.total) papers" -ForegroundColor Green
} catch {
    Write-Host "❌ Search POST Failed: $_" -ForegroundColor Red
}

Write-Host "`n✅ API Testing Complete!" -ForegroundColor Green
Write-Host "`nAccess API Docs at: http://localhost:8000/docs" -ForegroundColor Cyan

