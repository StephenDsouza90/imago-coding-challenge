### 1. Setup & Configuration
- [x] Set up Python project with FastAPI and required dependencies (elasticsearch-py, pydantic, etc.)
- [x] Configure Elasticsearch connection with given credentials
- [x] Create configuration management (environment variables for credentials)

### 2. Elasticsearch Integration
- [x] Implement connection to test Elasticsearch server
- [x] Create search function with basic query capabilities
- [x] Implement media URL construction logic (padding zeros, DB value handling)
- [x] Handle potential connection errors and timeouts

### 3. API Endpoints
- [x] Design RESTful endpoint `/search` (GET) - Keyword search and advance filtering
- [x] Add pagination support for search results
- [x] Implement health check endpoint (`/health`)

### 4. Data Processing
- [x] Implement data normalization for inconsistent fields
- [x] Create response models to standardize output format
- [x] Handle missing/empty fields gracefully
- [x] Add field mapping for better searchability
- [x] Implement request validation with Pydantic models
- [x] Use async / await keyword
- [ ] Improve searchability / data quality (handle mis-spelling or use regex)

### 5. Error Handling
- [x] Implement custom exception handling
- [x] Create proper HTTP error responses
- [x] Log errors for debugging
- [x] Handle Elasticsearch-specific errors
- [ ] Implement retry logic and fallback mechanisms

### 6. Testing
- [x] Write unit tests for core functions (URL generation, query building)
- [x] Injection attacks / input sanitization
- [x] Mock Elasticsearch responses for testing
- [x] Write end-to-end tests for API endpoints
- [x] Performance test

### 7. Monitoring, Logging & Caching
- [ ] Monitoring: Add performance metrics for search queries
- [x] Logging: Set up basic request logging
- [x] Caching: Implement caching

### 8. Deployment
- [x] Create Dockerfile
- [x] Create Docker Compose
- [x] Create K8s
- [x] Add basic GitHub Action CI/CD

### 9. Documentation
- [x] Write API documentation (OpenAPI/Swagger via FastAPI)
- [x] Create README with:
  - Setup instructions
  - API usage examples
  - Known limitations

### 10. Problem Identification & Solution
- [x] Identify at least one key issue
- [x] Document the problem and its impact
- [x] Propose solution with justification

### 11. Scalability, Maintainability & Security
- [x] Handle large volume of data
- [x] New provider and media
- [x] Connection pooling

### 12. Final Review
- [x] Check TODOs
- [ ] Code quality check
- [ ] Add code comments for complex logic
- [ ] Remove all passwords before final deployment
- [ ] Verify all requirements are addressed
- [ ] Prepare submission package
